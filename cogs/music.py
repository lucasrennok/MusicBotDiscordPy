import discord
from discord import app_commands
from discord.ext import commands
import random

from youtube_dl import YoutubeDL

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
    
        #all the music related stuff
        self.is_playing = False
        self.loop = False
        self.song_now_playing = []

        # 2d array containing [song, channel]
        self.music_queue = []
        self.music_queue_save = []
        self.music_queue_loop = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.prefix = "/"
        self.vc = ""

     #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.song_now_playing = self.music_queue[0]
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            if self.loop == True:
                self.music_queue = self.music_queue_loop

                #get the first url
                m_url = self.music_queue[0][0]['source']

                #remove the first element as you are currently playing it
                self.song_now_playing = self.music_queue[0]
                self.music_queue.pop(0)

                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            else:
                self.is_playing = False

    # infinite loop checking 
    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            
            #try to connect to voice channel if you are not already connected

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])
            
            print(self.music_queue)
            #remove the first element as you are currently playing it
            self.song_now_playing = self.music_queue[0]
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False
            await self.vc.disconnect()

    @app_commands.command(name="help",description="Mostra um guia de comandos do bot.")
    async def help(self,interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        helptxt = f"`{self.prefix}help` - Guia de comandos do bot!\n`{self.prefix}play ou {self.prefix}p` - Toca música ou coloca na fila\n`{self.prefix}queue` - Veja a fila de músicas que foram adicionadas para tocar\n`{self.prefix}skip` - Pule a música que está tocando para a próxima da fila\n`{self.prefix}pause` - Pausa a música e retoma música pausada\n`{self.prefix}resume` - Retoma música pausada\n`{self.prefix}stop` - Limpa fila e tira bot do canal de voz\n`{self.prefix}clear` - Limpa fila\n`{self.prefix}save_queue` - Salvar fila atual em playlist\n`{self.prefix}use_queue` - Usar playlist na fila\n`{self.prefix}clear_queue` - Limpa playlist salva\n`{self.prefix}loop` - Faz o loop das músicas tocando\n`{self.prefix}loop_queue` - Vê a playlist de músicas em loop\n\n_Comando para o dono do server:_\n`!!sync` - Sincronizar comandos do bot com o servidor"
        embedhelp = discord.Embed(
            colour = 1646116,#grey
            title=f'Comandos do {self.client.user.name}',
            description = helptxt
        )
        try:
            embedhelp.set_thumbnail(url=self.client.user.avatar.url)
        except:
            pass
        await interaction.followup.send(embed=embedhelp)


    @app_commands.command(name="play",description="Procura e toca uma música do Youtube")
    @app_commands.describe(
        busca = "Digite o nome da música no YouTube"
    )
    async def play(self, interaction:discord.Interaction,busca:str):
        await interaction.response.defer(thinking=True)
        query = busca
        
        try:
            voice_channel = interaction.user.voice.channel
        except:
        #if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Para tocar uma música, primeiro se conecte a um canal de voz.'
            )
            await interaction.followup.send(embed=embedvc)
            return
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                embedvc = discord.Embed(
                    colour= 12255232,#red
                    description = 'Algo deu errado! Tente mudar a playlist/vídeo ou escrever o nome dele novamente!'
                )
                await interaction.followup.send(embed=embedvc)
            else:
                embedvc = discord.Embed(
                    colour= 32768,#green
                    description = f"{interaction.user} adicionou a música **{song['title']}** à fila!"
                )
                await interaction.followup.send(embed=embedvc)
                self.music_queue.append([song, voice_channel])
                
                if self.is_playing == False:
                    await self.play_music()

    @app_commands.command(name="pause", description="Pausa uma música tocando")
    async def pause(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        if self.is_playing == False:
            embedvc = discord.Embed(
                colour= 12255232,#red
                description = 'Nenhuma música está tocando no momento!'
            )
            await interaction.followup.send(embed=embedvc)
        else:
            if self.vc.is_paused():
                self.vc.resume()
                embedvc = discord.Embed(
                    colour= 1646116,#grey
                    description = 'Música retomada!'
                )
                await interaction.followup.send(embed=embedvc)
            else:
                self.vc.pause()
                embedvc = discord.Embed(
                    colour= 1646116,#grey
                    description = 'Música pausada.'
                )
                await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="shuffle", description="Randomiza a fila")
    async def shuffle(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        tamanho = len(self.music_queue)
        if tamanho==0:
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Não existe músicas na fila para embaralhar'
            )
            await interaction.followup.send(embed=embedvc)
            return
        else:
            random.shuffle(self.music_queue)
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = f'Tem {tamanho} música na fila' if tamanho == 0 else f'Tem {tamanho} músicas na fila'
            )
            await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="save_queue", description="Salvar fila em playlist para loop ou usar depois")
    async def save_queue(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        self.music_queue_save = self.music_queue

    @app_commands.command(name="use_queue", description="Usar playlist salva de música")
    async def use_queue(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        self.music_queue = self.music_queue_save
        
    @app_commands.command(name="clear_queue", description="Limpa playlist")
    async def clear_queue(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        self.music_queue_save = []

    @app_commands.command(name="loop_queue", description="Mostra playlist do loop")
    async def loop_queue(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        retval = ""
        for i in range(0, len(self.music_queue_loop)):
            retval += f'**{i+1} - **' + self.music_queue_loop[i][0]['title'] + "\n"

        print(retval)
        if retval != "":
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"{retval}"
            )
            await interaction.followup.send(embed=embedvc)
        else:
            embedvc = discord.Embed(
                colour= 1646116,
                description = 'Não existe músicas na fila no momento.'
            )
            await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="loop", description="Loop na fila de músicas atual")
    async def loop(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        if self.loop == False:
            if len(self.music_queue) == 0:
                embedvc = discord.Embed(
                    colour= 1646116,#grey
                    description = 'Não tem músicas para fazer o loop'
                )
                await interaction.followup.send(embed=embedvc)
            else:
                self.loop = True
                self.music_queue_loop = self.music_queue
                self.music_queue_loop.insert(len(self.music_queue_loop), self.song_now_playing)
                embedvc = discord.Embed(
                    colour= 1646116,#grey
                    description = 'Loop ativo na playlist, ao final das músicas ele voltarará ao começo da fila salva no comando loop_queue'
                )
                await interaction.followup.send(embed=embedvc)
        else:
            self.loop = False
            self.music_queue_loop = []
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Loop de músicas desativado e playlist de loop excluída'
            )
            await interaction.followup.send(embed=embedvc)


    @app_commands.command(name="stop", description="Limpa fila e tira o bot do canal")
    async def stop(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        if self.vc != '' and (self.vc.is_playing() or self.vc.is_paused()):
            self.music_queue = []
            self.vc.stop()
            await self.vc.disconnect()
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Música parada e bot desconectado do canal de voz.'
            )
            await interaction.followup.send(embed=embedvc)
        else:
            self.music_queue = []
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'O bot não está em nenhum canal de voz para parar a música.'
            )
            await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="clear", description="Limpa fila")
    async def clear(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        if len(self.music_queue) > 0:
            self.music_queue = []
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Fila de músicas limpada!'
            )
            await interaction.followup.send(embed=embedvc)
        else:
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Fila já está vazia.'
            )
            await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="resume", description="Retoma música pausada")
    async def resume(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        if self.is_playing == False:
            embedvc = discord.Embed(
                colour= 12255232,#red
                description = 'Nenhuma música está tocando no momento!'
            )
            await interaction.followup.send(embed=embedvc)
        else:
            if self.vc.is_paused():
                self.vc.resume()
                embedvc = discord.Embed(
                    colour= 1646116,#grey
                    description = 'Música retomada!'
                )
                await interaction.followup.send(embed=embedvc)
            else:
                embedvc = discord.Embed(
                    colour= 1646116,#grey
                    description = 'Nenhuma música pausada.'
                )
                await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="p",description="Toca uma música")
    @app_commands.describe(
        busca = "Digite o nome da música"
    )
    async def p(self, interaction:discord.Interaction,busca:str):
        await interaction.response.defer(thinking=True)
        query = busca
        
        try:
            voice_channel = interaction.user.voice.channel
        except:
        #if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            embedvc = discord.Embed(
                colour= 1646116,#grey
                description = 'Para tocar uma música, primeiro se conecte a um canal de voz.'
            )
            await interaction.followup.send(embed=embedvc)
            return
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                embedvc = discord.Embed(
                    colour= 12255232,#red
                    description = 'Algo deu errado! Tente mudar a playlist/vídeo ou escrever o nome dele novamente!'
                )
                await interaction.followup.send(embed=embedvc)
            else:
                embedvc = discord.Embed(
                    colour= 32768,#green
                    description = f"{interaction.user} adicionou a música **{song['title']}** à fila!"
                )
                await interaction.followup.send(embed=embedvc)
                self.music_queue.append([song, voice_channel])
                
                if self.is_playing == False:
                    await self.play_music()

    @app_commands.command(name="queue",description="Mostra as atuais músicas da fila.")
    async def q(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f'**{i+1} - **' + self.music_queue[i][0]['title'] + "\n"

        print(retval)
        if retval != "":
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"{retval}"
            )
            await interaction.followup.send(embed=embedvc)
        else:
            embedvc = discord.Embed(
                colour= 1646116,
                description = 'Não existe músicas na fila no momento.'
            )
            await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="skip",description="Pula a atual música que está tocando.")
    @app_commands.default_permissions(manage_channels=True)
    async def skip(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        if self.vc != "" and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music()
            embedvc = discord.Embed(
                colour= 1646116, #grey
                description = "Você pulou a música."
            )
            await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="jump",description="Coloca uma música para a primeira posição da fila")
    @app_commands.default_permissions(manage_channels=True)
    async def jump(self, interaction:discord.Interaction,posicao:str):
        await interaction.response.defer(thinking=True)
        aux = self.music_queue[0]
        self.music_queue[0] = self.music_queue[posicao]
        self.music_queue[posicao] = self.music_queue[0]

        embedvc = discord.Embed(
            colour= 1646116, #grey
            description = "Música colocada no começo da fila, pode skipar para a próxima ou esperar ela."
        )
        await interaction.followup.send(embed=embedvc)
        

    @skip.error #Erros para kick
    async def skip_error(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, commands.MissingPermissions):
            embedvc = discord.Embed(
                colour= 12255232,
                description = f"Você precisa da permissão **Gerenciar canais** para pular músicas."
            )
            await interaction.followup.send(embed=embedvc)     
        else:
            raise error

async def setup(client):
    await client.add_cog(music(client))
    