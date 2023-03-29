# ライブラリをインポート
import discord
import configparser
import os
import requests
import sys
from yt_dlp import YoutubeDL
from colorama import init, Fore, Style

# coloramaを初期化
init()

# 変数の設定
status = "SimpleMusicBot v1.4 For Google Colaboratory"
bot_version: str = "v1.4 For Google Colaboratory"
config_version: int = 3
smb_info = Fore.BLUE + "[SMB-Info]" + Style.RESET_ALL
smb_debug = Fore.GREEN + "[SMB-Debug]" + Style.RESET_ALL
smb_warning = Fore.YELLOW + "[SMB-Warning]" + Style.RESET_ALL
smb_error = Fore.RED + "[SMB-Error]" + Style.RESET_ALL
error_404 = "discord.ApplicationContext.respondでdiscord.errors.NotFoundが発生しました。"
error_invoke = "discord.ApplicationContext.respondでdiscord.errors.ApplicationCommandInvokeErrorが発生しました。"
config_file_name = "config.ini"

# 新バージョンの確認
response = requests.get('https://api.github.com/repos/ni-302/SimpleMusicBot-GoogleColaboratory/releases/latest')
latest_release = response.json()
latest_version: str = latest_release['tag_name']
if latest_version != bot_version:
    print(f'{smb_info}新バージョンが利用可能です!')
    print(f'{smb_info}実行中のバージョン : {bot_version}')
    print(f'{smb_info}最新バージョン : {latest_version}')
    print(f'{smb_info}リンク : https://github.com/ni-302/SimpleMusicBot-GoogleColaboratory/releases/tag/{latest_version}')

# configparserの設定
config = configparser.ConfigParser()
path = config_file_name
is_file = os.path.isfile(path)
if is_file:
    config.read(config_file_name)
    print(f'{smb_info}{config_file_name}を読み込みました!')
    config_status = "Found"
else:
    print(f'{smb_error}{config_file_name}が見つかりません!')
    config_status = "NotFound"

# configを生成する関数
def config_gen():
    while True:
        config_token = "YOUR_TOKEN_HERE"
        try:
            user_input = input("botのトークンを入力してください。: ") 
        except KeyboardInterrupt:
            sys.exit()
        if user_input is not None:
            config_token = user_input
            break
    config['config'] = {
    'config_version' : f'{config_version}',
    'token': f'{config_token}',
    'default_volume': '0.2',
    'DevMode': 'False'
    }
    with open(config_file_name, 'w') as configfile:
        config.write(configfile)

# configがあるか確認してなければ生成する
if config_status == "NotFound":
    print(f'{smb_info}{config_file_name}を生成します。')
    config_gen()

# トークンの設定
try:
    TOKEN = config.get('config', 'token')
except configparser.NoSectionError:
    print(f'{smb_error}{config_file_name}からのトークンの取得に失敗しました。')

try:
    if TOKEN == "YOUR_TOKEN_HERE":
        print(f'{smb_error}トークンが適切に設定されていません!')
        token_status = "Imappropriate"
        token_status_tf = False
    else:
        if TOKEN is None:
            print(f'{smb_error}トークンが空です。')
            token_status = "None"
            token_status_tf = False
        else:
            token_status = "OK"
            token_status_tf = True
except NameError:
    print(f'{smb_error}トークンが正しく設定されていません!')
    token_status = "Imappropriate"
    token_status_tf = False

# 音量の初期値の設定
try:
    dvol = config.getfloat('config', 'default_volume')
    print(f'{smb_info}default_volumeを{dvol}に設定しました。')
except configparser.NoSectionError:
    print(f'{smb_error}{config_file_name}からのdefault_volumeの取得に失敗しました。')
    dvol = 0.2
    print(f'{smb_info}default_volumeを0.2に設定しました。')

# デバッグ設定
try:
    Config_Dev_Mode = config.getboolean('config', 'DevMode')
    Dev_Mode: bool = Config_Dev_Mode
    print(f'{smb_info}DevModeを{Dev_Mode}に設定しました。')
except configparser.NoSectionError:
    Dev_Mode = False
    print(f'{smb_error}{config_file_name}からのDevModeの取得に失敗しました。')
except configparser.NoOptionError:
    Dev_Mode = False
    print(f'{smb_error}{config_file_name}からのDevModeの取得に失敗しました。')
except NameError:
    Dev_Mode = False
    print(f'{smb_error}{config_file_name}からDevModeの設定が読み込めませんでした。')
if Dev_Mode == True and token_status_tf == False:
    TOKEN = "YOUR_DEVBOT_TOKEN_HERE"

# コンフィグをアップデートする関数
def config_update():
    config_token = TOKEN
    config['config'] = {
    'config_version' : f'{config_version}',
    'token': f'{config_token}',
    'default_volume': f'{dvol}',
    'DevMode': f'{Dev_Mode}'
    }
    with open(config_file_name, 'w') as configfile:
        config.write(configfile)

# コンフィグのバージョン確認
try:
    now_config_version = config.getint('config', 'config_version')
except configparser.NoSectionError:
    now_config_version = -1
    print(f'{smb_error}{config_file_name}からのconfigのバージョンの取得に失敗しました。')
except configparser.NoOptionError:
    now_config_version = -1
    print(f'{smb_error}{config_file_name}からのconfigのバージョンの取得に失敗しました。')
if now_config_version == config_version:
    config_version_status = "OK"
else:
    config_version_status = "Imappropriate"
    print(f'{smb_warning}configのバージョンが違います!')
    print(f'{smb_info}configをアップデートします。')
    config_update()

# クライアントの設定
client = discord.Bot(intents=discord.Intents.all())

# yt-dlpのオプションの設定
options = {
            'format': 'best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp4',
                'preferredquality': '192'
            }],
            'verbose': 'True',
            'flat-playlist': 'True'
        }

# キューを保存するところ
nop = []
queue = []

# 関数の設定
def next(vc):
    if queue:
        with YoutubeDL(options) as opt:
            try:
                qnp = nop.pop(0)
            except Exception:
                pass
            qnp = queue.pop(0)
            nop.append(qnp)
            info = opt.extract_info(qnp, download=False)
            vc.play(discord.FFmpegPCMAudio(info['url']), after=lambda e: next(vc))
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = dvol
    else:
        vc.stop()

def debug_novc():
    print (f'\n\n\n\n\n{smb_debug}\n\nSimpleMusicBot{bot_version}\nby ni-302\n\n[Config]\nConfig Version:{now_config_version}\nConfig Version Status:{config_version_status}\nToken Status:{token_status}\nDefault Volume{dvol}\n\n[status]\nDevMode:{Dev_Mode}\nNowPlaying:{nop}Queue:{queue}\nyt-dlp Options:{options}\n\n\n\n\n')

# 起動時の設定
@client.event
async def on_ready():
    presence = discord.Game(status)
    await client.change_presence(activity=presence)
    print(f'{smb_info}ステータスを{status}に変更しました。')
    print(f'{smb_info}SimpleMusicBot{bot_version}起動完了')
    if Dev_Mode is True:
        debug_novc()

# コマンドの設定
@client.command(name ="url", description="指定したURLの音楽を再生します。")
async def play(ctx: discord.ApplicationContext, url: str):
    voice_channel = ctx.author.voice.channel
    vc = ctx.voice_client
    if vc is None:
        vc = await voice_channel.connect()
        queue.append(url)
        next(vc)
        try:
            await ctx.respond(f'{url} を再生します。')
        except discord.errors.NotFound:
            print(f'{smb_error}{error_404}')
        except discord.errors.ApplicationCommandInvokeError:
            print(f'{smb_error}{error_invoke}')
    else:
        queue.append(url)
        await ctx.respond(f'キューに {url} を追加しました。')
        if not vc.is_playing():
            next(vc)

@client.command(name ="yt", description="YouTubeでキーワード検索を行い、結果の一番上を再生します。")
async def search(ctx: discord.ApplicationContext, *, query: str):
    if ctx.voice_client is None:
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()
    vc = ctx.voice_client
    with YoutubeDL(options) as opt:
        query = f'ytsearch1:{query}'
        info = opt.extract_info(query, download=False)
        url = info['entries'][0]['webpage_url']
        queue.append(url)
        durl = url
        if vc.is_playing():
            try:
                await ctx.respond(f'キューに {durl} を追加しました。')
            except discord.errors.NotFound:
                print(f'{smb_error}{error_404}')
            except discord.errors.ApplicationCommandInvokeError:
                print(f'{smb_error}{error_invoke}')
        if not vc.is_playing():
            try:
                await ctx.respond(f'{durl} を再生します。')
            except discord.errors.NotFound:
                print(f'{smb_error}{error_404}')
            except discord.errors.ApplicationCommandInvokeError:
                print(f'{smb_error}{error_invoke}')
            next(vc)


@client.command(name ="stp", description="再生を停止します。")
async def stop(ctx: discord.ApplicationContext):
    vc = ctx.voice_client
    if vc is not None:
        vc.stop()
        await vc.disconnect()
        await ctx.respond('再生を停止しました。')

@client.command(name ="vol", description="音量を調整します(パーセント入力、デフォルトは100%)")
async def volume(ctx: discord.ApplicationContext, volume: float):
    vc = ctx.voice_client
    if vc is not None:
        vc.source.volume = volume / 100 * dvol
        await ctx.respond(f'音量を {volume} %に設定します。')

@client.command(name ="skp", description="曲をスキップして、次の曲を再生します。")
async def skip(ctx: discord.ApplicationContext):
    vc = ctx.voice_client
    if vc is not None:
        vc.stop()
        await ctx.respond('スキップしました。')

@client.command(name ="debug", description="Send debug to console.")
async def debug(ctx: discord.ApplicationContext):
    try:
        await ctx.respond('Sending debug to console is complete!')
    except TypeError:
        print(f'{smb_error}A TypeError occurred on ctx.respond.')
    if ctx.voice_client is None:
        pstatus = False
    else:
        pstatus = True
    print (f'\n\n\n\n\n{smb_debug}\n\nSimpleMusicBot{bot_version}\nby ni-302\n\n[Config]\nConfig Version:{now_config_version}\nConfig Version Status:{config_version_status}\nToken Status:{token_status}\nDefault Volume{dvol}\n\n[status]\nDevMode:{Dev_Mode}\nNowPlaying:{nop}Queue:{queue}\nPlaying:{pstatus}\nyt-dlp Options:{options}\nvc={ctx.voice_client}\n\n\n\n\n')

@client.command(name ="nop", description="現在再生している曲のURLを取得します。")
async def nowplaying(ctx: discord.ApplicationContext):
    try:
        await ctx.respond(f'再生中 : {nop}')
    except discord.errors.NotFound:
        print(f'{smb_error}{error_404}')
    except discord.errors.ApplicationCommandInvokeError:
        print(f'{smb_error}{error_invoke}')

@client.command(name ="qe", description="現在のキューを取得します。")
async def nowplaying(ctx: discord.ApplicationContext):
    try:
        await ctx.respond(f'現在のキュー : {queue}')
    except discord.errors.NotFound:
        print(f'{smb_error}{error_404}')
    except discord.errors.ApplicationCommandInvokeError:
        print(f'{smb_error}{error_invoke}')

@client.command(name ="nsp", description="指定した番号の曲をスキップします。")
async def numberskip(ctx: discord.ApplicationContext, number : int):
    nspnumber = number - 1
    nsp = queue.pop(nspnumber)
    try:
        await ctx.respond(f'{number}番目のキュー ({nsp}) を削除しました。')
    except discord.errors.NotFound:
        print(f'{smb_error}{error_404}')
    except discord.errors.ApplicationCommandInvokeError:
        print(f'{smb_error}{error_invoke}')

# BOTを実行
try:
    client.run(TOKEN)
except NameError:
    print(f'{smb_error}Botの起動に失敗しました。トークンの設定を確認してください。')
except discord.errors.LoginFailure:
    print(f'{smb_error}Botの起動に失敗しました。(discord.errors.LoginFailure)')
