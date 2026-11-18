import unittest
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace
from aiohttp.test_utils import TestClient, TestServer
from aiogram import Bot, Dispatcher
from main import create_app, start, profile, help_message


class BotTests(unittest.IsolatedAsyncioTestCase):
    async def test_unconfigured_service(self):
        async with TestClient(TestServer(create_app(token=""))) as client:
            r = await client.get('/health')
            self.assertEqual(r.status, 200)
            self.assertEqual(await r.json(), {'status': 'ok', 'bot_configured': False})
            self.assertEqual((await client.post('/telegram/webhook', json={})).status, 404)

    async def test_commands(self):
        message = SimpleNamespace(answer=AsyncMock(), from_user=SimpleNamespace(id=123))
        for handler in (start, profile, help_message):
            await handler(message)
        self.assertEqual(message.answer.await_count, 3)
        self.assertIn('123', message.answer.await_args_list[1].args[0])

    async def test_webhook_authentication(self):
        import hashlib
        token = '123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi'
        secret = hashlib.sha256(('kenaigo-webhook:' + token).encode()).hexdigest()
        with patch.object(Bot, 'get_me', new=AsyncMock(return_value=SimpleNamespace(username='Kenaigo_bot'))), \
             patch.object(Bot, 'set_my_commands', new=AsyncMock()), \
             patch.object(Bot, 'set_webhook', new=AsyncMock(return_value=True)) as register, \
             patch.object(Dispatcher, 'feed_webhook_update', new=AsyncMock(return_value=None)) as feed:
            async with TestClient(TestServer(create_app(token=token, external_url='https://example.com'))) as client:
                register.assert_awaited_once()
                self.assertEqual(register.await_args.kwargs['secret_token'], secret)
                r = await client.post('/telegram/webhook', json={'update_id': 1})
                self.assertEqual(r.status, 401)
                feed.assert_not_awaited()
                r = await client.post('/telegram/webhook', json={'update_id': 2},
                                      headers={'X-Telegram-Bot-Api-Secret-Token': secret})
                self.assertEqual(r.status, 200)
                feed.assert_awaited_once()
