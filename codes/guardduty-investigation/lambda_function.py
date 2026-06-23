import json
import os
import urllib.request

import boto3
from aws_durable_execution_sdk_python import (
    DurableContext,
    durable_execution,
    durable_step,
)
from aws_durable_execution_sdk_python.config import Duration

guardduty = boto3.client('guardduty')
translate = boto3.client('translate')
secretsmanager = boto3.client('secretsmanager')

DETECTOR_ID = os.environ['DETECTOR_ID']
SLACK_SECRET_NAME = os.environ['SLACK_SECRET_NAME']

def get_slack_webhook_url():
    resp = secretsmanager.get_secret_value(SecretId=SLACK_SECRET_NAME)
    secret = json.loads(resp['SecretString'])
    return secret.get('url') or secret.get('webhook_url') or resp['SecretString']

RISK_EMOJI = {
    'Critical': ':rotating_light:',
    'High': ':red_circle:',
    'Medium': ':large_yellow_circle:',
    'Low': ':large_blue_circle:',
    'Info': ':white_circle:',
}


def defang_urls(text):
    import re
    # URL スキームを無効化: http -> hxxp
    text = re.sub(r'https?://', lambda m: m.group().replace('http', 'hxxp'), text)
    # ドメイン・ホスト名のドットを [.] に置換（英数字・ハイフンで構成されるラベル間のドット）
    text = re.sub(r'(?<=[a-zA-Z0-9])\.((?:[a-zA-Z0-9-]+\.)*[a-zA-Z]{2,})', lambda m: '[.]' + m.group(1), text)
    return text


def translate_to_ja(text):
    if not text:
        return text
    resp = translate.translate_text(
        Text=text,
        SourceLanguageCode='en',
        TargetLanguageCode='ja',
    )
    return defang_urls(resp['TranslatedText'])


@durable_step
def start_investigation(step_context, account_id, finding_type):
    resp = guardduty.create_investigation(
        DetectorId=DETECTOR_ID,
        TriggerPrompt=f"Analyze organization account with account id: {account_id}. Triggered by finding type: {finding_type}.",
    )
    step_context.logger.info(f"Investigation started: {resp['InvestigationId']}")
    return resp['InvestigationId']


@durable_step
def get_investigation_status(step_context, investigation_id):
    resp = guardduty.get_investigation(
        DetectorId=DETECTOR_ID,
        InvestigationId=investigation_id,
    )
    inv = resp['Investigation']
    step_context.logger.info(f"Investigation status: {inv['Status']}")
    summary = json.loads(inv.get('Summary', '{}'))
    recommendations = summary.get('recommendations', {}).get('items', [])
    return {
        'status': inv['Status'],
        'riskLevel': inv.get('RiskLevel', ''),
        'confidence': inv.get('Confidence', ''),
        'risk': inv.get('Risk', ''),
        'summary': inv.get('Summary', '{}'),
        'recommendations': recommendations,
    }


@durable_step
def send_slack_notification(step_context, result, finding_type, account_id, finding_id):
    status = result.get('status', 'UNKNOWN')

    if status == 'FAILED':
        payload = {
            'text': (
                f':warning: *GuardDuty Investigation が失敗しました*\n'
                f'Finding: `{finding_type}`\n'
                f'Finding ID: `{finding_id}`\n'
                f'Account: `{account_id}`'
            )
        }
    else:
        risk_level = result.get('riskLevel', 'Unknown')
        confidence = result.get('confidence', 'Unknown')
        risk_desc = translate_to_ja(result.get('risk', ''))
        emoji = RISK_EMOJI.get(risk_level, ':white_circle:')

        try:
            summary = json.loads(result.get('summary', '{}'))
            key_obs = summary.get('keyObservations', {})
            narrative = translate_to_ja(key_obs.get('narrative', ''))
            observations = [translate_to_ja(obs) for obs in key_obs.get('observations', [])]
        except (json.JSONDecodeError, AttributeError):
            narrative = ''
            observations = []

        blocks = [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': f'{emoji} GuardDuty Investigation 完了',
                },
            },
            {
                'type': 'section',
                'fields': [
                    {'type': 'mrkdwn', 'text': f'*Finding Type*\n`{finding_type}`'},
                    {'type': 'mrkdwn', 'text': f'*Account*\n`{account_id}`'},
                    {'type': 'mrkdwn', 'text': f'*Risk Level*\n{emoji} {risk_level}'},
                    {'type': 'mrkdwn', 'text': f'*Confidence*\n{confidence}'},
                ],
            },
        ]

        if risk_desc:
            blocks.append({
                'type': 'section',
                'text': {'type': 'mrkdwn', 'text': f'*リスク評価*\n{risk_desc}'},
            })

        if narrative:
            blocks.append({
                'type': 'section',
                'text': {'type': 'mrkdwn', 'text': f'*概要*\n{narrative}'},
            })

        if observations:
            obs_text = '\n'.join(f'• {obs}' for obs in observations[:5])
            blocks.append({
                'type': 'section',
                'text': {'type': 'mrkdwn', 'text': f'*主な観察内容*\n{obs_text}'},
            })

        recommendations = result.get('recommendations', [])
        immediate = [r for r in recommendations if r.get('priority') == 'IMMEDIATE']
        short_term = [r for r in recommendations if r.get('priority') == 'SHORT_TERM']
        rec_items = immediate[:3] + short_term[:2]
        if rec_items:
            PRIORITY_LABEL = {'IMMEDIATE': '緊急', 'SHORT_TERM': '短期'}
            rec_lines = []
            for r in rec_items:
                pri = PRIORITY_LABEL.get(r.get('priority', ''), r.get('priority', ''))
                title = translate_to_ja(r.get('title', ''))
                rec_lines.append(f'[{pri}] {title}')
            blocks.append({
                'type': 'section',
                'text': {'type': 'mrkdwn', 'text': f'*推奨事項*\n' + '\n'.join(f'• {l}' for l in rec_lines)},
            })

        payload = {'blocks': blocks}

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        get_slack_webhook_url(),
        data=data,
        headers={'Content-Type': 'application/json'},
    )
    urllib.request.urlopen(req)


@durable_execution
def lambda_handler(event, context: DurableContext):
    detail = event['detail']
    finding_id = detail['id']
    account_id = detail['accountId']
    finding_type = detail['type']

    investigation_id = context.step(start_investigation(account_id, finding_type))

    while True:
        context.wait(Duration.from_minutes(1))
        result = context.step(get_investigation_status(investigation_id))
        if result['status'] in ('COMPLETED', 'FAILED'):
            break

    context.step(send_slack_notification(result, finding_type, account_id, finding_id))

    return result
