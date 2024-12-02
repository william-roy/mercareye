# notify.py

from discord_webhook import DiscordWebhook, DiscordEmbed

from config import config

def sendNotification(search_name, item_id, item_name, 
                     item_price, item_thumbnail_url=''):
    
    print('Sending notification...')

    webhook = DiscordWebhook(
        url=config['NOTIFICATIONS']['DiscordWebhookURL'],
        username='mercareye')

    embed = DiscordEmbed(
        title=item_name, 
        description=f'https://buyee.jp/mercari/item/{item_id}', 
        color='ff0211')
    
    embed.set_author(name=search_name)
    embed.add_embed_field(name='Price', value=item_price)
    embed.set_thumbnail(url=item_thumbnail_url)

    webhook.add_embed(embed)
    response = webhook.execute()

    print('Notification sent...')

    # Other webhooks, email, etc.?