import discord
import ast
from difflib import SequenceMatcher
import pickle
from discord import ui, app_commands
from discord.ext import tasks
import time
import tabulate
import random
import pyrebase
import json
import sqlite3

try:
    with open('config_copy.json','r') as f:
        config = json.load(f)

except Exception as e:
    if isinstance(e, FileNotFoundError):
        raise FileNotFoundError('No config file found')
    else:
        raise TypeError('File is not a valid json')

db = {}
int_abv = {'ag': 'Agility','int': 'Intelligence','per':'Perception','const':'Constant Vigilance'}
abv = {'ws':'Weapon Skill','bs': 'Ballistic Skill','s':'Strength','t':'Toughness','ag': 'Agility','int': 'Intelligence','per':'Perception','wp':'Willpower','fel':'Fellowship','ifl':'Influence'}
sev_five = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3, 12: 3, 13: 3, 14: 4, 15: 4, 16: 4, 17: 4, 18: 4, 19: 5, 20: 5, 21: 5, 22: 5, 23: 5, 24: 5, 25: 6, 26: 6, 27: 6, 28: 6, 29: 6, 30: 6, 31: 7, 32: 7, 33: 7, 34: 7, 35: 7, 36: 7, 37: 7, 38: 7, 39: 8, 40: 8, 41: 8, 42: 8, 43: 8, 44: 8, 45: 8, 46: 8, 47: 9, 48: 9, 49: 9, 50: 9, 51: 9, 52: 9, 53: 9, 54: 9, 55: 9, 56: 10, 57: 10, 58: 10, 59: 11, 60: 11, 61: 11, 62: 11, 63: 11, 64: 11, 65: 11, 66: 11, 67: 11, 68: 12, 69: 12, 70: 12, 71: 12, 72: 12, 73: 13, 74: 13, 75: 13, 76: 13, 77: 13, 78: 13, 79: 14, 80: 14, 81: 14, 82: 14, 83: 15, 84: 15, 85: 15, 86: 15, 87: 16, 88: 16, 89: 16, 90: 16, 91: 17, 92: 17, 93: 17, 94: 17, 95: 17, 96: 17, 97: 17, 98: 17, 99: 17, 100: 18}
sev_five_notes = {1: 'The Gibbering: The psyker screams in pain as uncontrolled Warp energies surge through his unprepared mind. He must make a Challenging (+0) Willpower test or be Stunned for 1d5 rounds.', 2: 'Warp Burn: A violent burst of energy from the Warp smashes into the psyker’s mind, sending him reeling. He suffers 2d5 Energy damage, ignoring Toughness bonus and Armour, and is Stunned for 1d5 rounds.', 3: 'Psychic Concussion: With a crack of energy, the psyker is knocked unconscious for 1d5 rounds, and everyone within 3d10 metres must make an Ordinary (+10) Willpower test or be Stunned for one round.', 4: 'Psy Blast: There is an explosion of power and the psyker is thrown 3d10 metres into the air, plummeting to the ground moments later (see page 243 for rules concerning falling damage).', 5: 'Soul Sear: Warp power courses through the psyker’s body, scorching his soul. The psyker cannot use any psychic powers for the next hour, and gains 2d5 Corruption points.', 6: 'Locked In: The power cages the psyker’s mind in an ethereal prison, tormented by visions of the Warp. The psyker falls to the ground Prone and Unconscious. At the beginning of each of his turns until he breaks free, he must spend a Full Action to make a Difficult (–10) Willpower test. If he succeeds, his mind is freed and restored to his body, haunted by his experiences but otherwise unharmed.', 7: 'Chronological Incontinence: Time warps around the psyker. He winks out of existence and reappears in 1d10 rounds (or one minute in narrative time) in the exact location. He suffers one point of permanent Toughness and Intelligence damage as his body and mind rebel against the experience, and gains 1d5 Corruption points.', 8: 'Psychic Mirror: The psyker’s power is turned back on him. Resolve the power’s effects, but the power targets the psyker instead. If the power is beneficial, it deals 1d10+5 Energy damage (ignoring Armour) to the psyker’s Body instead of having its normal effect.', 9: 'Warp Whispers: The voices of Daemons fill the air within 4d10 metres of the psyker, whispering terrible secrets and shocking truths. Each character in range (including the psyker) must make a Hard (–20) Willpower test or gain 1d5 Corruption points and suffer an equal amount of Willpower damage. Whether or not the psyker passes the Willpower test, he suffers an additional 1d5+5 Willpower damage.', 10: 'Vice Versa: The psyker’s mind is thrown out of his body and into another nearby creature or person. The psyker and a random living creature (friend or foe, but not a Daemon, machine, or other “soulless” entity) within 50 metres swap consciousness for 1d10 rounds. Each creature retains its Weapon Skill, Ballistic Skill, Intelligence, Perception, Willpower, and Fellowship during the swap, but uses the other characteristics of the host body. If either body is slain, the effect ends immediately and both parties return to their original bodies. Both suffer 1d5 Intelligence damage from the experience. If there are no creatures within range, the psyker becomes catatonic for 1d5 rounds while his mind wanders the Warp. This journey inflicts 1d10 Willpower damage, 1d10 Intelligence damage, and 1d10 Corruption points.', 11: 'Dark Summoning: The Empyrean buckles and tears at the arrogance of the psyker, and a Plaguebearer (see page 415) or another lesser Daemon at the GM’s discretion rips its way into existence. The pestilent fiend appears within 3d10 metres of the psyker, for a number of rounds equal to 1d5 plus the psyker’s Toughness bonus. The psyker’s turn immediately ends, and the Daemon takes its turn immediately. It detests the psyker and focuses all of its attacks upon the fool who unwittingly summoned it. It does not attack anyone else, even if others attack it; if the psyker is slain, it returns back to the Warp, satisfied with its kill.', 12: 'Rending the Veil: The air vibrates with images of cackling Daemons and the kaleidoscopic fabric of the Warp is rendered visible to mortal eyes. All sentient creatures within 1d100 metres must test against Fear (2). The psyker must test against Fear (4) instead. This effect lasts for 1d5 rounds. ', 13: 'Blood Rain: A psychic storm erupts, covering an area of 5d10 metres. Each character in range (including the psyker) must make a Challenging (+0) Strength test or be knocked Prone. In addition to howling winds and rains of blood, any psychic powers used in the area for 1d5 rounds automatically invoke Perils of the Warp, in addition to any Psychic Phenomena caused. The psyker gains 1d5+1 Corruption points. ', 14: 'Cataclysmic Blast: The psyker’s power overloads, arcing out in great bolts of Warp energy. Each character within 1d10 metres (including the psyker) takes 1d10 Energy damage with a Pen of 5. The psyker may not Dodge this, or stop the attack with a force field (see page 168). In addition, all of the psyker’s clothing, armour, and gear is destroyed, leaving him naked and smoking on the ground, and he cannot use further powers for 1d5 hours after the event.', 15: 'Mass Incursion: Chaos Furies (page 417) emerge from the Warp, hungry for souls. Each character within 1d100 metres of the psyker (including himself) must make a Hard (–20) Willpower test or gain 1d10 Corruption and Insanity points, and suffer 1d10 Willpower damage. Each character who succeeds is attacked physically by a Fury, which departs after 1d5 rounds.', 16: 'Reality Quake: Reality buckles around the psyker, and an area radiating out 3d10 metres from him is sundered: solid objects alternately rot, burn, and freeze, and everyone and everything in the area suffers a single hit for 2d10 Rending damage that ignores Armour and cannot be Dodged. Warded objects, Daemons, and Untouchables halve the damage they would suffer.', 17: "Grand Incursion: A great and terrible Warp entity takes an interest in the psyker's flesh. Use the profile for Putricifex, Herald of Nurgle from page 416 (or another suitably powerful Daemon) to represent the attacker, who instantly makes an Opposed Very Hard (–20) Willpower test against the psyker. If the Daemon wins, it possesses the psyker's body for 1 hour per degree by which it won the test. The psyker gains 2d10 Insanity and Corruption points and is controlled by the Daemon until the effect ends. If he dies while possessed, the Daemon physically manifests for the remainder of the effect's duration. If the psyker wins the test, he suffers 2d10 Toughness damage, and forever adds +10 to all rolls on Table 6–2: Psychic Phenomena and Table 6–3: Perils of the Warp, as his polluted body now serves as a Warp conduit.", 18: 'Annihilation: The psyker is immediately burned to ashes by the screaming fires of the Immaterium or dragged into the deepest maelstrom of the Warp. He cannot burn Fate to avert this death and is irrevocably destroyed. There is a chance that a daemonic entity of some sort appears in his place—the type of Daemon is determined by the GM, based on how powerful the psyker was, as more powerful psykers draw more powerful Daemons. The percentage chance that the Daemon appears is equal to the psyker’s Willpower characteristic (roll a 1d100, if the result is equal to or under the characteristic, the Daemon appears).'}
dub={1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 3, 8: 3, 9: 4, 10: 4, 11: 4, 12: 5, 13: 5, 14: 5, 15: 6, 16: 6, 17: 6, 18: 7, 19: 7, 20: 7, 21: 8, 22: 8, 23: 8, 24: 9, 25: 9, 26: 9, 27: 10, 28: 10, 29: 10, 30: 11, 31: 11, 32: 11, 33: 12, 34: 12, 35: 12, 36: 13, 37: 13, 38: 13, 39: 14, 40: 14, 41: 14, 42: 15, 43: 15, 44: 15, 45: 16, 46: 16, 47: 16, 48: 17, 49: 17, 50: 17, 51: 18, 52: 18, 53: 18, 54: 19, 55: 19, 56: 19, 57: 20, 58: 20, 59: 20, 60: 21, 61: 21, 62: 21, 63: 22, 64: 22, 65: 22, 66: 23, 67: 23, 68: 23, 69: 24, 70: 24, 71: 24, 72: 25, 73: 25, 74: 25, 75: 26}
dub_notes = {1: 'Dark Foreboding: A faint breeze blows past the psyker and those near him, and everyone gets the feeling that somewhere in the galaxy something unfortunate just happened.', 2: 'Warp Echo: For a few moments, all noises cause echoes, regardless of the surroundings.', 3: 'Unholy Stench: The air around the psyker becomes permeated with a bizarre and foul smell.', 4: 'Mind Warp: The psyker suffers a –5 penalty to Willpower tests until the start of his next turn as his own inherent phobias, suspicions, and hatreds surge to the surface of his mind in a wave of unbound emotion.', 5: 'Hoarfrost: The temperature plummets for an instant, and a thin coating of frost forms to cover everything within 3d10 metres.', 6: 'Aura of Taint: All animals within 1d100 metres become spooked and agitated; characters can use the Psyniscience skill to pinpoint the psyker as the cause.', 7: 'Memory Worm: All people within line of sight of the psyker forget some trivial fact or minor personal memory.', 8: 'Spoilage: Food and drink go bad in a 5d10 metre radius.', 9: 'Haunting Breeze: Winds whip up around the psyker for a few moments, blowing light objects around and guttering fires within 3d10 metres.', 10: 'Veil of Darkness: For a brief moment (effectively, until the end of the round), the area within 3d10 metres is plunged into immediate and impenetrable darkness.', 11: 'Distorted Reflections: Mirrors and other reflective surfaces within a radius of 5d10 metres distort or shatter.', 12: 'Breath Leech: Each character (including the psyker) within a 3d10 metre radius becomes short of breath for one round and cannot make any Run or Charge actions.', 13: 'Daemonic Mask: For a fleeting moment, the psyker takes on a daemonic appearance and gains the Fear (1) trait until the start of the next turn. However, he also gains 1 Corruption point.', 14: 'Unnatural Decay: All plant life within 3d10 metres of the psyker withers and dies.', 15: 'Spectral Gale: Howling winds erupt around the psyker, requiring each character (including the psyker) within 4d10 metres to make an Easy (+30) Agility or Strength test to avoid being knocked Prone.', 16: 'Bloody Tears: Blood weeps from stone and wood within 3d10 metres of the psyker. If there are any paintings, pict-displays, statues, or other representations of people inside this area, they appear to be crying blood.', 17: 'The Earth Protests: The ground suddenly shakes, and each character (including the psyker) within a 5d10 metre radius must make an Ordinary (+10) Agility test or be knocked down.', 18: 'Actinic Discharge: Static electricity fills the air within 5d10 metres causing hair to stand on end and unprotected electronics to short out, while the psyker is wreathed in eldritch lightning. The GM is free to resolve the specifics as needed, perhaps using Table 5–4: Haywire Field Effects (see page 147) to provide guidance.', 19: 'Warp Ghosts: Ghostly apparitions fill the air within 3d10 metres around the psyker, flying about and howling in pain for a few brief moments. Each character in the radius (except the psyker himself) must test against Fear (1).', 20: 'Falling Upwards: Everything within 2d10 metres of the psyker (including the psyker himself) rises 1d10 metres into the air as gravity briefly ceases. Almost immediately, everything crashes back to earth, suffering falling damage as appropriate for the distances fallen.', 21: 'Banshee Howl: A shrill keening rings out across the immediate area, shattering glass and forcing each living creature able to hear it (including the psyker) to pass a Challenging (+0) Toughness test or be deafened for 1d10 rounds.', 22: 'The Furies: The Psyker is assailed by unseen horrors. He is slammed to the ground and suffers 1d5 Impact damage (ignoring Armour, but not Toughness bonus) and he must test against Fear (2).', 23: 'Shadow of the Warp: For a split second, the world changes in appearance, and everyone within 1d100 metres has a brief but horrific glimpse of the shadow of the Warp. Each character in the area (including the psyker) must make a Difficult (–10) Willpower test or gain 1d5 Corruption points.', 24: 'Tech Scorn: The machine spirits reject these unnatural ways. All un-warded technology within 5d10 metres malfunctions momentarily, and all ranged weapons jam (see page 224). Each character (including the psyker) withing that range with cybernetic implants mustpass an Ordinary (+10) Toughness test or suffer 1d5 Rending damage, ignoring Toughness bonus and Armour.', 25: 'Warp Madness: A violent ripple of tainted discord causes all characters (except the psyker) within 2d10 metres to make a Difficult (–10) Willpower test; each character who fails gains 1d5 Corruption points and becomes Frenzied for 1 round (see page 127).', 26: 'Perils of the Warp: The Warp opens in a wild maelstrom of unnatural energy. Roll on Table 6–3: Perils of the Warp (page 197).'}

cache = set()

@tasks.loop(seconds = 3) # repeat after every 10 seconds
async def autosave():
    c.execute("UPDATE DATA SET dd = ?",(json.dumps(db),))
    # with open('root.json','wb') as f:
    #     pickle.dump(db,f)
    #     if config['isFirebase']:
    #         time.sleep(7)
    #         storage.child('root.json').put('root.json')

#more data handling here

class client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False
        self.type = type

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await bot.sync()
            self.synced= True
        self.add_view(intRollView())
        print(f"Logged in as {self.user}")
        autosave.start()
        

    async def on_guild_join(self, guild:discord.Guild):
        db['server_db'][guild.id] = {'admin':None, 'gm':None, 'toEdit':True, 'toUse':True,'toCreate':True, 'toDelete':True, 'ruleSet':"Standard"}
    
    async def on_guild_remove(self, guild):
        db['server_db'].pop(guild.id)
    
    def canDo(self, user:discord.Member,action,data=None):
        guild = db['server_db'][user.guild.id]
        roles = [role.id for role in user.roles]
        Check1 = False
        if guild[f'to{action}']:
            Check1= True 
        if guild['admin']:
            if guild['admin'] in roles:
                Check1= True
        if guild['gm']:
            if guild['gm'] in roles:
                Check1= True
        if user.guild_permissions.administrator:
            Check1= True
        if action!='Create':
            if data['origin'] == user.guild.id:
                Check2 = True
            elif data['owner'] == user.id:
                Check2 = True
            else:
                Check2 = False
            return Check1*Check2
        else:
            return Check1

aclient = client()
bot = app_commands.CommandTree(aclient)

#-------------------------------------------------------------
# Character Creation Sheets - Create
#-------------------------------------------------------------
class page1(ui.Modal, title = "Character Sheet | Overview"):
    def __init__(self,user):
        super().__init__()
        self.user = user
    answer1= ui.TextInput(label="● Name:", style=discord.TextStyle.short, placeholder="What is the Character's Name")
    answer2= ui.TextInput(label="● Source Book:", style=discord.TextStyle.short, placeholder='What book is the character from? Dark Heresy, Black Crusade, or one of the other FFG books?')
    answer3= ui.TextInput(label="● Backstory:", style=discord.TextStyle.long, max_length=1000, placeholder='Once upon a time in the lands of Sector Thettra...')

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Overview", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer1.label, value=f'{self.answer1}', inline=False)
        embed.add_field(name='● Played by:', value=f'<@{self.user.id}>', inline=False)
        embed.add_field(name=self.answer2.label, value=f'{self.answer2}', inline=False)
        embed.add_field(name='● Experience:', value='0', inline=False)
        embed.add_field(name=self.answer3.label, value=f'{self.answer3}', inline=False)
        embed.set_footer(text='Character Sheet | page 1')
        char = {}
        char['owner'] = self.user.id
        char['name'] = str(self.answer1)
        char['source'] = str(self.answer2)
        char['exp'] = 0
        char['bio'] = str(self.answer3)
        char['user'] = interaction.user
        await interaction.response.send_message(embed=embed,view=nextButton1(char))

class nextButton1(ui.View):
    def __init__(self, char):
        super().__init__()
        self.char = char
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='NextButton')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.char['user'].id:
            await inter.response.send_modal(page2(inter.message, self.char))
        
class page2(ui.Modal, title = "Character Sheet | Characteristics(a)"):
    def __init__(self, msg:discord.Message, char:dict):
        super().__init__()
        self.msg = msg
        self.char = char
    answer1= ui.TextInput(label="● Weapon Skill (WS):", style=discord.TextStyle.short, placeholder="Assign a numeric value")
    answer2= ui.TextInput(label="● Ballistic Skill (BS):", style=discord.TextStyle.short, placeholder="Assign a numeric value")
    answer3= ui.TextInput(label="● Strength (S):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer4= ui.TextInput(label="● Toughness (T):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer5= ui.TextInput(label="● Agility (AG):", style=discord.TextStyle.short,placeholder="Assign a numeric value")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Characteristics(a)", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer1.label, value=f'{self.answer1}', inline=False)
        embed.add_field(name=self.answer2.label, value=f'{self.answer2}', inline=False)
        embed.add_field(name=self.answer3.label, value=f'{self.answer3}', inline=False)
        embed.add_field(name=self.answer4.label, value=f'{self.answer4}', inline=False)
        embed.add_field(name=self.answer5.label, value=f'{self.answer5}', inline=False)
        embed.set_footer(text='Character Sheet | page 2')
        answers = [self.answer1,self.answer2,self.answer3,self.answer4,self.answer5]
        for answer in answers:
            if not str(answer).isnumeric():
                await interaction.response.send_message("Please provide only numeric values")
                return
        self.char['ws'] = str(self.answer1)
        self.char['bs'] = str(self.answer2)
        self.char['s'] = str(self.answer3)
        self.char['t'] = str(self.answer4)
        self.char['ag'] = str(self.answer5)
        await interaction.response.send_message(embed=embed, view=nextButton2a(char=self.char))
        await self.msg.edit(view=None)

class nextButton2a(ui.View):
    def __init__(self, char):
        super().__init__()
        self.char = char
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='NextButton2a')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.char['user'].id:
            await inter.response.send_modal(page2a(inter.message,self.char))

class page2a(ui.Modal, title = "Character Sheet | Characteristics(a)"):
    def __init__(self, msg:discord.Message, char:dict):
        super().__init__()
        self.msg = msg
        self.char = char
    answer1= ui.TextInput(label="● Unnatural Weapon Skill (WS):", style=discord.TextStyle.short, placeholder="Assign a numeric value")
    answer2= ui.TextInput(label="● Unnatural Ballistic Skill (BS):", style=discord.TextStyle.short, placeholder="Assign a numeric value")
    answer3= ui.TextInput(label="● Unnatural Strength (S):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer4= ui.TextInput(label="● Unnatural Toughness (T):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer5= ui.TextInput(label="● Unnatural Agility (AG):", style=discord.TextStyle.short,placeholder="Assign a numeric value")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Characteristics(a)", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer1.label, value=f'{self.answer1}', inline=False)
        embed.add_field(name=self.answer2.label, value=f'{self.answer2}', inline=False)
        embed.add_field(name=self.answer3.label, value=f'{self.answer3}', inline=False)
        embed.add_field(name=self.answer4.label, value=f'{self.answer4}', inline=False)
        embed.add_field(name=self.answer5.label, value=f'{self.answer5}', inline=False)
        embed.set_footer(text='Character Sheet | page 2 (a)')
        answers = [self.answer1,self.answer2,self.answer3,self.answer4,self.answer5]
        for answer in answers:
            if not str(answer).isnumeric():
                await interaction.response.send_message("Please provide only numeric values")
                return
        self.char['uws'] = str(self.answer1)
        self.char['ubs'] = str(self.answer2)
        self.char['us'] = str(self.answer3)
        self.char['ut'] = str(self.answer4)
        self.char['uag'] = str(self.answer5)
        await interaction.response.send_message(embed=embed, view=nextButton2(char=self.char))
        await self.msg.edit(view=None)

class nextButton2(ui.View):
    def __init__(self, char):
        super().__init__()
        self.char = char
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='NextButton2')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.char['user'].id:
            await inter.response.send_modal(page3(inter.message,self.char))

class page3(ui.Modal, title = "Character Sheet | Characteristics(b)"):
    def __init__(self, msg:discord.Message, char:dict):
        super().__init__()
        self.msg = msg
        self.char = char
    answer6= ui.TextInput(label="● Intelligence (INT):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer7= ui.TextInput(label="● Perception (PER):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer8= ui.TextInput(label="● Willpower (WP):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer9= ui.TextInput(label="● Fellowship (FEL):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer10= ui.TextInput(label="● Influence (IFL):", style=discord.TextStyle.short,placeholder="Assign a numeric value")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Characteristics(b)", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer6.label, value=f'{self.answer6}', inline=False)
        embed.add_field(name=self.answer7.label, value=f'{self.answer7}', inline=False)
        embed.add_field(name=self.answer8.label, value=f'{self.answer8}', inline=False)
        embed.add_field(name=self.answer9.label, value=f'{self.answer9}', inline=False)
        embed.add_field(name=self.answer10.label, value=f'{self.answer10}', inline=False)
        answers = [self.answer6,self.answer7,self.answer8,self.answer9,self.answer10]
        for answer in answers:
            if not str(answer).isnumeric():
                await interaction.response.send_message("Please provide only numeric values")
                return
        self.char['int'] = str(self.answer6)
        self.char['per'] = str(self.answer7)
        self.char['wp'] = str(self.answer8)
        self.char['fel'] = str(self.answer9)
        self.char['ifl'] = str(self.answer10)
        embed.set_footer(text='Character Sheet | page 3')
        await self.msg.edit(view=None)
        await interaction.response.send_message(embed=embed, view=nextButton3a(self.char))

class nextButton3a(ui.View):
    def __init__(self, char):
        super().__init__()
        self.char = char
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='NextButton3a')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.char['user'].id:
            await inter.response.send_modal(page3a(inter.message, self.char))

class page3a(ui.Modal, title = "Character Sheet | Characteristics(b)"):
    def __init__(self, msg:discord.Message, char:dict):
        super().__init__()
        self.msg = msg
        self.char = char
    answer6= ui.TextInput(label="● Unnatural Intelligence (INT):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer7= ui.TextInput(label="● Unnatural Perception (PER):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer8= ui.TextInput(label="● Unnatural Willpower (WP):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer9= ui.TextInput(label="● Unnatural Fellowship (FEL):", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer10= ui.TextInput(label="● Unnatural Influence (IFL):", style=discord.TextStyle.short,placeholder="Assign a numeric value")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Characteristics(b)", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer6.label, value=f'{self.answer6}', inline=False)
        embed.add_field(name=self.answer7.label, value=f'{self.answer7}', inline=False)
        embed.add_field(name=self.answer8.label, value=f'{self.answer8}', inline=False)
        embed.add_field(name=self.answer9.label, value=f'{self.answer9}', inline=False)
        embed.add_field(name=self.answer10.label, value=f'{self.answer10}', inline=False)
        answers = [self.answer6,self.answer7,self.answer8,self.answer9,self.answer10]
        for answer in answers:
            if not str(answer).isnumeric():
                await interaction.response.send_message("Please provide only numeric values")
                return
        self.char['uint'] = str(self.answer6)
        self.char['uper'] = str(self.answer7)
        self.char['uwp'] = str(self.answer8)
        self.char['ufel'] = str(self.answer9)
        self.char['uifl'] = str(self.answer10)
        embed.set_footer(text='Character Sheet | page 3 (a)')
        await self.msg.edit(view=None)
        await interaction.response.send_message(embed=embed, view=nextButton3(self.char))

class nextButton3(ui.View):
    def __init__(self, char):
        super().__init__()
        self.char = char
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='NextButton3')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.char['user'].id:
            await inter.response.send_modal(page4(inter.message, self.char))

class page4(ui.Modal, title = "Character Sheet | Characteristics(c)"):
    def __init__(self, msg:discord.Message, char:dict):
        super().__init__()
        self.msg = msg
        self.char = char
    answer6= ui.TextInput(label="● Insanity (INS)", style=discord.TextStyle.short,placeholder="Assign a numeric value")
    answer7= ui.TextInput(label="● Corruption (COR)", style=discord.TextStyle.short,placeholder="Assign a numeric value")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Characteristics(c)", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer6.label, value=f'{self.answer6}', inline=False)
        embed.add_field(name=self.answer7.label, value=f'{self.answer7}', inline=False)
        answers = [self.answer6,self.answer7]
        for answer in answers:
            if not str(answer).isnumeric():
                await interaction.response.send_message("Please provide only numeric values")
                return
        self.char['ins'] = str(self.answer6)
        self.char['cor'] = str(self.answer7)
        embed.set_footer(text='Character Sheet | page 3')
        await self.msg.edit(view=None)
        await interaction.response.send_message(embed=embed, view=nextButton4(self.char))

class nextButton4(ui.View):
    def __init__(self, char):
        super().__init__()
        self.char = char
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='NextButton3')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.char['user'].id:
            await inter.response.send_modal(page5(inter.message, self.char))

class page5(ui.Modal, title = "Character Sheet | Conditions"):
    def __init__(self, msg:discord.Message, char:dict):
        super().__init__()
        self.msg = msg
        self.char = char
    d = "None"
    c = 5
    answer6= ui.TextInput(label="● Fate Threshold:", style=discord.TextStyle.short,default=c,placeholder='Maximum Threshold')
    answer7= ui.TextInput(label="● Wounds Threshold:", style=discord.TextStyle.short,default=c,placeholder='Maximum Threshold')
    answer8= ui.TextInput(label="● Fatigue Threshold:", style=discord.TextStyle.short,default=c,placeholder='Maximum Threshold')
    answer9= ui.TextInput(label="● Critical Damage:", style=discord.TextStyle.short,default=d)
    answer10= ui.TextInput(label="● Conditions:", style=discord.TextStyle.short,default=d)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = f"Character Sheet | Conditions", color=discord.Color.from_str('#ffdd70'))
        if len(self.char['ag'])>1:
            bonus = int(self.char['ag'][0]) 
            move = f"Half: {bonus*1} | Full: {bonus*2} | Charge: {bonus*3} | Run: {bonus*6}"
        else:
            move = 'Half: 1/2 | Full: 1 | Charge: 2 | Run: 3'
        embed.add_field(name='● Movement:', value=move, inline=False)
        embed.add_field(name=self.answer6.label, value=f'{self.answer6}', inline=False)
        embed.add_field(name=self.answer7.label, value=f'{self.answer7}', inline=False)
        embed.add_field(name=self.answer8.label, value=f'{self.answer8}', inline=False)
        embed.add_field(name=self.answer9.label, value=f'{self.answer9}', inline=False)
        embed.add_field(name=self.answer10.label, value=f'{self.answer10}', inline=False)
        self.char['con_fp'] = str(self.answer6)
        self.char['con_ws'] = str(self.answer7)
        self.char['con_fa'] = str(self.answer8)
        self.char['con_cd'] = str(self.answer9)
        self.char['con'] = str(self.answer10)
        self.char['img_url'] = 'https://media.discordapp.net/attachments/1022782030326550540/1028500866921156618/Bot_Profile_Default2.png'
        #---------------
        # Visibility ids
        # 0 - Public 
        # 1 - Server specific mode
        # 2 - private
        self.char['visib'] = 2
        self.char['whitelist'] = [] #empty list to allow whitelist other server if user changes the visibility of the character
        self.char['origin'] = interaction.guild.id
        embed.set_footer(text='Character Sheet | page 4')
        await self.msg.edit(view=None)
        await interaction.response.send_message(content='Character Creation Complete, Please use `/image` to add a art to your character',embed=embed)
        self.char.pop('user')
        if self.char['owner'] in db['user_db']:
            db['user_db'][self.char['owner']]['char_list'].append(self.char)
        else:
            db['user_db'][self.char['owner']] = {'char_list': [self.char],'weapons':{}}

#-------------------------------------------------------------
# Character Sheets - Edits
#-------------------------------------------------------------

class Editpage1(ui.Modal, title = "Editing | Character Sheet | Overview"):
    def __init__(self,char:str,flow=False,doer=None):
        super().__init__()
        self.char = char
        self.doer = doer
        self.flow = flow
        self.answer1= ui.TextInput(label="● Name:", style=discord.TextStyle.short, default=self.char['name'],placeholder="What is the Character's Name")
        self.answer2= ui.TextInput(label="● Source Book:", style=discord.TextStyle.short,default=self.char['source'], placeholder='What book is the character from? Dark Heresy, Black Crusade, or one of the other FFG books?')
        self.answer3= ui.TextInput(label="● Backstory:", style=discord.TextStyle.long,default=self.char['bio'], max_length=1000, placeholder='Once upon a time in the lands of Sector Thettra...')
        self.add_item(self.answer1)
        self.add_item(self.answer2)
        self.add_item(self.answer3)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Overview", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer1.label, value=f'{self.answer1}', inline=False)
        embed.add_field(name='● Played by:', value=f'<@{self.char["owner"]}>', inline=False)
        embed.add_field(name=self.answer2.label, value=f'{self.answer2}', inline=False)
        embed.add_field(name='● Experience:', value=self.char['exp'], inline=False)
        embed.add_field(name=self.answer3.label, value=f'{self.answer3}', inline=False)
        embed.set_footer(text='Character Sheet | page 1')
        self.char['name'] = str(self.answer1)
        self.char['source'] = str(self.answer2)
        self.char['bio'] = str(self.answer3)
        if self.flow:

            await interaction.response.send_message(embed=embed,view=EditnextButton1(self.char,self.doer))
        else:
            embed.set_footer(text='Edit Complete!')
            await interaction.response.send_message(embed=embed)

class EditnextButton1(ui.View):
    def __init__(self, char,doer):
        super().__init__()
        self.char = char
        self.doer = doer
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='EditNextButton1')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.doer:
            await inter.response.send_modal(Editpage2(inter.message, self.char,flow=True,doer=self.doer))
        
class Editpage2(ui.Modal, title = "Editing | Characteristics(a)"):
    def __init__(self, msg:discord.Message=None, char:dict=None,flow:bool=False,doer=None):
        super().__init__()
        self.flow = flow
        self.child = True
        self.msg = msg
        self.char = char
        self.doer = doer
        self.answer1= ui.TextInput(label="● Weapon Skill (WS):", style=discord.TextStyle.short,default=self.char['ws'] ,placeholder="Assign a numeric value")
        self.answer2= ui.TextInput(label="● Ballistic Skill (BS):", style=discord.TextStyle.short,default=self.char['bs'] ,placeholder="Assign a numeric value")
        self.answer3= ui.TextInput(label="● Strength (S):", style=discord.TextStyle.short,default=self.char['s'],placeholder="Assign a numeric value")
        self.answer4= ui.TextInput(label="● Toughness (T):", style=discord.TextStyle.short,default=self.char['t'],placeholder="Assign a numeric value")
        self.answer5= ui.TextInput(label="● Agility (AG):", style=discord.TextStyle.short,default=self.char['ag'],placeholder="Assign a numeric value")
        self.add_item(self.answer1)
        self.add_item(self.answer2)
        self.add_item(self.answer3)
        self.add_item(self.answer4)
        self.add_item(self.answer5)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Characteristics(a)", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer1.label, value=f'{self.answer1}', inline=False)
        embed.add_field(name=self.answer2.label, value=f'{self.answer2}', inline=False)
        embed.add_field(name=self.answer3.label, value=f'{self.answer3}', inline=False)
        embed.add_field(name=self.answer4.label, value=f'{self.answer4}', inline=False)
        embed.add_field(name=self.answer5.label, value=f'{self.answer5}', inline=False)
        embed.set_footer(text='Character Sheet | page 2')
        answers = [self.answer1,self.answer2,self.answer3,self.answer4,self.answer5]
        for answer in answers:
            if not str(answer).isnumeric():
                await interaction.response.send_message("Please provide only numeric values")
                return
        self.char['ws'] = str(self.answer1)
        self.char['bs'] = str(self.answer2)
        self.char['s'] = str(self.answer3)
        self.char['t'] = str(self.answer4)
        self.char['ag'] = str(self.answer5)
        if self.flow or self.child:
            await interaction.response.send_message(embed=embed, view=EditnextButton2a(char=self.char,doer=self.doer,child=self.child,flow=self.flow))
            if self.flow:
                await self.msg.edit(view=None)
        else:
            embed.set_footer(text='Edit Complete!')
            await interaction.response.send_message(embed=embed)

class EditnextButton2a(ui.View):
    def __init__(self, char,doer,child,flow):
        super().__init__()
        self.char = char
        self.doer = doer
        self.child = child
        self.flow = flow
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='EditNextButton2a')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.doer:
            if self.child and not self.flow:
                await inter.response.send_modal(Editpage2a(inter.message,self.char,flow=False,doer=self.doer))
                await inter.message.edit(view=None)
            else:
                await inter.response.send_modal(Editpage2a(inter.message,self.char,flow=True,doer=self.doer))

class Editpage2a(ui.Modal, title = "Editing | Characteristics(a)"):
    def __init__(self, msg:discord.Message=None, char:dict=None,flow:bool=False,doer=None):
        super().__init__()
        self.flow = flow
        self.msg = msg
        self.char = char
        self.doer = doer
        self.answer1= ui.TextInput(label="● Unnatural Weapon Skill (WS):", style=discord.TextStyle.short,default=self.char['uws'] ,placeholder="Assign a numeric value")
        self.answer2= ui.TextInput(label="● Unnatural Ballistic Skill (BS):", style=discord.TextStyle.short,default=self.char['ubs'] ,placeholder="Assign a numeric value")
        self.answer3= ui.TextInput(label="● Unnatural Strength (S):", style=discord.TextStyle.short,default=self.char['us'],placeholder="Assign a numeric value")
        self.answer4= ui.TextInput(label="● Unnatural Toughness (T):", style=discord.TextStyle.short,default=self.char['ut'],placeholder="Assign a numeric value")
        self.answer5= ui.TextInput(label="● Unnatural Agility (AG):", style=discord.TextStyle.short,default=self.char['uag'],placeholder="Assign a numeric value")
        self.add_item(self.answer1)
        self.add_item(self.answer2)
        self.add_item(self.answer3)
        self.add_item(self.answer4)
        self.add_item(self.answer5)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Characteristics(a)", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer1.label, value=f'{self.answer1}', inline=False)
        embed.add_field(name=self.answer2.label, value=f'{self.answer2}', inline=False)
        embed.add_field(name=self.answer3.label, value=f'{self.answer3}', inline=False)
        embed.add_field(name=self.answer4.label, value=f'{self.answer4}', inline=False)
        embed.add_field(name=self.answer5.label, value=f'{self.answer5}', inline=False)
        embed.set_footer(text='Character Sheet | page 2 (a)')
        answers = [self.answer1,self.answer2,self.answer3,self.answer4,self.answer5]
        for answer in answers:
            if not str(answer).isnumeric():
                await interaction.response.send_message("Please provide only numeric values")
                return
        self.char['uws'] = str(self.answer1)
        self.char['ubs'] = str(self.answer2)
        self.char['us'] = str(self.answer3)
        self.char['ut'] = str(self.answer4)
        self.char['uag'] = str(self.answer5)
        if self.flow:

            await interaction.response.send_message(embed=embed, view=EditnextButton2(char=self.char,doer=self.doer))
            await self.msg.edit(view=None)
        else:
            embed.set_footer(text='Edit Complete!')
            await interaction.response.send_message(embed=embed)

class EditnextButton2(ui.View):
    def __init__(self, char,doer):
        super().__init__()
        self.char = char
        self.doer = doer
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='EditNextButton2')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.doer:
            await inter.response.send_modal(Editpage3(inter.message,self.char,flow=True,doer=self.doer))

class Editpage3(ui.Modal, title = "Editing | Characteristics(b)"):
    def __init__(self, msg:discord.Message=None, char:dict=None,flow:bool=True,doer=None):
        super().__init__()
        self.msg = msg
        self.char = char
        self.child = True
        self.flow = flow
        self.doer = doer
        self.answer6= ui.TextInput(label="● Intelligence (INT):", style=discord.TextStyle.short,default=self.char['int'],placeholder="Assign a numeric value")
        self.answer7= ui.TextInput(label="● Perception (PER):", style=discord.TextStyle.short,default=self.char['per'],placeholder="Assign a numeric value")
        self.answer8= ui.TextInput(label="● Willpower (WP):", style=discord.TextStyle.short,default=self.char['wp'],placeholder="Assign a numeric value")
        self.answer9= ui.TextInput(label="● Fellowship (FEL):", style=discord.TextStyle.short,default=self.char['fel'],placeholder="Assign a numeric value")
        self.answer10= ui.TextInput(label="● Influence (IFL):", style=discord.TextStyle.short,default=self.char['ifl'],placeholder="Assign a numeric value")
        self.add_item(self.answer6)
        self.add_item(self.answer7)
        self.add_item(self.answer8)
        self.add_item(self.answer9)
        self.add_item(self.answer10)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Characteristics(b)", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer6.label, value=f'{self.answer6}', inline=False)
        embed.add_field(name=self.answer7.label, value=f'{self.answer7}', inline=False)
        embed.add_field(name=self.answer8.label, value=f'{self.answer8}', inline=False)
        embed.add_field(name=self.answer9.label, value=f'{self.answer9}', inline=False)
        embed.add_field(name=self.answer10.label, value=f'{self.answer10}', inline=False)
        answers = [self.answer6,self.answer7,self.answer8,self.answer9,self.answer10]
        for answer in answers:
            if not str(answer).isnumeric():
                await interaction.response.send_message("Please provide only numeric values")
                return
        self.char['int'] = str(self.answer6)
        self.char['per'] = str(self.answer7)
        self.char['wp'] = str(self.answer8)
        self.char['fel'] = str(self.answer9)
        self.char['ifl'] = str(self.answer10)
        embed.set_footer(text='Character Sheet | page 3')
        if self.flow or self.child:
            await self.msg.edit(view=None)
            if self.flow:
                await interaction.response.send_message(embed=embed, view=EditnextButton3a(self.char,self.doer,self.child,self.flow))
        else:
            embed.set_footer(text='Edit Complete!')
            await interaction.response.send_message(embed=embed)

class EditnextButton3a(ui.View):
    def __init__(self, char,doer,child,flow):
        super().__init__()
        self.char = char
        self.doer = doer
        self.flow = flow
        self.child = child
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='EditNextButton3a')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.doer:
            if self.child and not self.flow:
                await inter.response.send_modal(Editpage3a(inter.message,self.char,flow=False,doer=self.doer))
                await inter.message.edit(view=None)
            else:
                await inter.response.send_modal(Editpage3a(inter.message,self.char,flow=True,doer=self.doer))

class Editpage3a(ui.Modal, title = "Editing | Characteristics(b)"):
    def __init__(self, msg:discord.Message=None, char:dict=None,flow:bool=False,doer=None):
        super().__init__()
        self.msg = msg
        self.char = char
        self.flow = flow
        self.doer = doer
        self.answer6= ui.TextInput(label="● Unnatural Intelligence (INT):", style=discord.TextStyle.short,default=self.char['int'],placeholder="Assign a numeric value")
        self.answer7= ui.TextInput(label="● Unnatural Perception (PER):", style=discord.TextStyle.short,default=self.char['per'],placeholder="Assign a numeric value")
        self.answer8= ui.TextInput(label="● Unnatural Willpower (WP):", style=discord.TextStyle.short,default=self.char['wp'],placeholder="Assign a numeric value")
        self.answer9= ui.TextInput(label="● Unnatural Fellowship (FEL):", style=discord.TextStyle.short,default=self.char['fel'],placeholder="Assign a numeric value")
        self.answer10= ui.TextInput(label="● Unnatural Influence (IFL):", style=discord.TextStyle.short,default=self.char['ifl'],placeholder="Assign a numeric value")
        self.add_item(self.answer6)
        self.add_item(self.answer7)
        self.add_item(self.answer8)
        self.add_item(self.answer9)
        self.add_item(self.answer10)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Characteristics(b)", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer6.label, value=f'{self.answer6}', inline=False)
        embed.add_field(name=self.answer7.label, value=f'{self.answer7}', inline=False)
        embed.add_field(name=self.answer8.label, value=f'{self.answer8}', inline=False)
        embed.add_field(name=self.answer9.label, value=f'{self.answer9}', inline=False)
        embed.add_field(name=self.answer10.label, value=f'{self.answer10}', inline=False)
        answers = [self.answer6,self.answer7,self.answer8,self.answer9,self.answer10]
        for answer in answers:
            if not str(answer).isnumeric():
                await interaction.response.send_message("Please provide only numeric values")
                return
        self.char['uint'] = str(self.answer6)
        self.char['uper'] = str(self.answer7)
        self.char['uwp'] = str(self.answer8)
        self.char['ufel'] = str(self.answer9)
        self.char['uifl'] = str(self.answer10)
        embed.set_footer(text='Character Sheet | page 3 (a)')
        if self.flow:
            await self.msg.edit(view=None)
            await interaction.response.send_message(embed=embed, view=EditnextButton3(self.char,self.doer))
        else:
            embed.set_footer(text='Edit Complete!')
            await interaction.response.send_message(embed=embed)

class EditnextButton3(ui.View): 
    def __init__(self, char,doer):
        super().__init__()
        self.char = char
        self.doer = doer
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='EditNextButton3')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.doer:
            await inter.response.send_modal(Editpage4(inter.message, self.char,flow=True,doer=self.doer))

class Editpage4(ui.Modal, title = "Editing | Characteristics(c)"):
    def __init__(self, msg:discord.Message=None, char:dict=None,flow:bool=False,doer=None):
        super().__init__()
        self.msg = msg
        self.char = char
        self.flow = flow
        self.doer = doer
        self.answer6= ui.TextInput(label="● Insanity (INS)", style=discord.TextStyle.short,default=char['ins'],placeholder="Assign a numeric value")
        self.answer7= ui.TextInput(label="● Corruption (COR)", style=discord.TextStyle.short,default=self.char['cor'],placeholder="Assign a numeric value")
        self.add_item(self.answer6)
        self.add_item(self.answer7)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Character Sheet | Characteristics(c)", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer6.label, value=f'{self.answer6}', inline=False)
        embed.add_field(name=self.answer7.label, value=f'{self.answer7}', inline=False)
        answers = [self.answer6,self.answer7]
        for answer in answers:
            if not str(answer).isnumeric():
                await interaction.response.send_message("Please provide only numeric values")
                return
        self.char['ins'] = str(self.answer6)
        self.char['cor'] = str(self.answer7)
        embed.set_footer(text='Character Sheet | page 3')
        if self.flow:
            await self.msg.edit(view=None)
            await interaction.response.send_message(embed=embed, view=EditnextButton4(self.char,self.doer))
        else:
            embed.set_footer(text='Edit Complete!')
            await interaction.response.send_message(embed=embed)

class EditnextButton4(ui.View):
    def __init__(self, char,doer):
        super().__init__()
        self.char = char
        self.doer = doer
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='EditNextButton3')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id == self.doer:
            await inter.response.send_modal(Editpage5(inter.message, self.char,flow=True,doer=self.doer))

class Editpage5(ui.Modal, title = "Editing | Character Sheet | Conditions"):
    def __init__(self, msg:discord.Message=None, char:dict=None, flow:bool=None,doer=None):
        super().__init__()
        self.msg = msg
        self.char = char
        self.flow = flow
        d = "None"
        c = 5
        self.doer = doer
        self.answer6= ui.TextInput(label="● Fate Threshold:", style=discord.TextStyle.short,default=char['con_fa'],placeholder='Maximum Threshold')
        self.answer7= ui.TextInput(label="● Wounds Threshold:", style=discord.TextStyle.short,default=char['con_ws'],placeholder='Maximum Threshold')
        self.answer8= ui.TextInput(label="● Fatigue Threshold:", style=discord.TextStyle.short,default=char['con_fa'],placeholder='Maximum Threshold')
        self.answer9= ui.TextInput(label="● Critical Damage:", style=discord.TextStyle.short,default=char['con_cd'])
        self.answer10= ui.TextInput(label="● Conditions:", style=discord.TextStyle.short,default=char['con'])
        self.add_item(self.answer6)
        self.add_item(self.answer7)
        self.add_item(self.answer8)
        self.add_item(self.answer9)
        self.add_item(self.answer10)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = f"Character Sheet | Conditions", color=discord.Color.from_str('#ffdd70'))
        if len(self.char['ag'])>1:
            bonus = int(self.char['ag'][0]) 
            move = f"Half: {bonus*1} | Full: {bonus*2} | Charge: {bonus*3} | Run: {bonus*6}"
        else:
            move = 'Half: 1/2 | Full: 1 | Charge: 2 | Run: 3'
        embed.add_field(name='● Movement:', value=move, inline=False)
        embed.add_field(name=self.answer6.label, value=f'{self.answer6}', inline=False)
        embed.add_field(name=self.answer7.label, value=f'{self.answer7}', inline=False)
        embed.add_field(name=self.answer8.label, value=f'{self.answer8}', inline=False)
        embed.add_field(name=self.answer9.label, value=f'{self.answer9}', inline=False)
        embed.add_field(name=self.answer10.label, value=f'{self.answer10}', inline=False)
        self.char['con_fp'] = str(self.answer6)
        self.char['con_ws'] = str(self.answer7)
        self.char['con_fa'] = str(self.answer8)
        self.char['con_cd'] = str(self.answer9)
        self.char['con'] = str(self.answer10)
        embed.set_footer(text='Character Sheet | page 4')
        if self.flow:
            await self.msg.edit(view=None)
            await interaction.response.send_message(content='Character Edit Complete, Please use `/image` to change/add an art to your character',embed=embed)
        else:
            embed.set_footer(text='Edit Complete!')
            await interaction.response.send_message(embed=embed)

#-------------------------------------------------------------
# Character Management Classes
#-------------------------------------------------------------

class ViewEmbed():
    def __init__(self,char,user:discord.User,char_id):
        self.char = char
        self.char_id = char_id
        self.user = user
    def page(self,pos):
        if pos==1:
            return self.page1()
        elif pos == 2:
            return self.page2()
        elif pos==3:
            return self.page3()
    def page1(self):
        emb = discord.Embed(title=f"{'(Active) ' if self.char_id == 0 else ''}{self.char['name'].capitalize()} | Overview", color=discord.Color.from_str('#ffdd70'))
        emb.set_image(url = self.char['img_url'])
        emb.add_field(name='● Name:', value=self.char['name'], inline=False)
        emb.add_field(name='● Source:', value=self.char['source'], inline=False)
        emb.add_field(name='● Experience:', value=self.char['exp'], inline=False)
        emb.add_field(name='● Backstory:', value=self.char['bio'], inline=False)
        emb.set_footer(text = 'Page 1/3')
        # owner = aclient.get_user(self.char['owner'])
        # emb.set_thumbnail(url=owner.avatar.url)
        return emb

    def page2(self):
        emb = discord.Embed(title=f"{'(Active) ' if self.char_id == 0 else ''}{self.char['name'].capitalize()} | Characteristics", color=discord.Color.from_str('#ffdd70'))
        emb.add_field(name='● Weapon Skill (WS):', value=self.char['ws'])
        emb.add_field(name='● Intelligence (INT):', value=self.char['int'])
        emb.add_field(name='● Ballastic Skill (BS):', value=self.char['bs'])
        emb.add_field(name='● Perception (PER):', value=self.char['per'])
        emb.add_field(name='● Strength (S):', value=self.char['s'])
        emb.add_field(name='● Willpower (WP):', value=self.char['wp'])
        emb.add_field(name='● Toughness (T):', value=self.char['t'])
        emb.add_field(name='● Fellowship (FEL):', value=self.char['fel'])
        emb.add_field(name='● Agility (AG):', value=self.char['ag'])
        emb.add_field(name='● Influence (IFL):', value=self.char['ifl'])
        emb.set_footer(text = 'Page 2/3')
        emb.set_thumbnail(url=self.char['img_url'])
        return emb

    def page3(self):
        emb = discord.Embed(title=f"{'(Active) ' if self.char_id == 0 else ''}{self.char['name'].capitalize()} | Conditions", color=discord.Color.from_str('#ffdd70'))
        if len(self.char['ag'])>1:
            bonus = int(self.char['ag'][0]) 
            move = f"Half: {bonus*1} | Full: {bonus*2} | Charge: {bonus*3} | Run: {bonus*6}"
        else:
            move = 'Half: 1/2 | Full: 1 | Charge: 2| Run: 3'
        emb.add_field(name='● Movement:', value=move, inline=False)
        emb.add_field(name='● Fate Threshold:', value=self.char['con_fp'], inline=False)
        emb.add_field(name='● Wounds Threshold:', value=self.char['con_ws'], inline=False)
        emb.add_field(name='● Fatigue Threshold:', value=self.char['con_fa'], inline=False)
        emb.add_field(name='● Critical Damage:', value=self.char['con_cd'], inline=False)
        emb.add_field(name='● Conditions:', value=self.char['con'], inline=False)
        emb.set_footer(text = 'Page 3/3')
        emb.set_thumbnail(url=self.char['img_url'])
        return emb

class ViewNavBar(ui.View):
    def __init__(self, pos=1, embed:ViewEmbed=None):
        super().__init__()
        self.pos = pos
        self.embed = embed
    @discord.ui.button(label='Back', style=discord.ButtonStyle.green, custom_id='NavBack')
    async def back(self, inter:discord.Interaction, button:ui.Button):
        self.pos-=1
        if self.pos==0:
            self.pos=3
        elif self.pos==4:
            self.pos=1
        await inter.response.edit_message(view=self,embed=self.embed.page(pos=self.pos))
    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, custom_id='NavNext')
    async def next(self, inter:discord.Interaction, button:ui.Button):
        self.pos+=1
        if self.pos==0:
            self.pos=3
        elif self.pos==4:
            self.pos=1
        await inter.response.edit_message(view=self,embed=self.embed.page(pos=self.pos))

class EditEmbed():
    def embed(char):
        emb = discord.Embed(title=f"Character Edit Menu | {char['name']}",color=discord.Color.from_str('#ffdd70'))
        emb.add_field(name='● Overview:', value='Basic character overview\nName,Source,Back story',inline=False)
        emb.add_field(name='● Chrt (a):', value='Characteristics section (a)\nWeapon, Ballastic, Strength, Toughness, Agility',inline=False)
        emb.add_field(name='● Chrt (b):', value='Characteristics section (b)\nIntelligence, Perception, Willpower, Fellowship, Influence',inline=False)
        emb.add_field(name='● Chrt (c):', value='Characteristics section (c)\nInsanity, Corruption',inline=False)
        emb.add_field(name='● Conditions:', value='Character Condition\nFate, Wounds, Fatigue Threshold, Critical Damage ',inline=False)
        return emb

class EditSelectBar(ui.View):
    def __init__(self,char,user):
        super().__init__()
        self.embed = EditEmbed.embed(char)
        self.char = char
        self.user = user
    
    @discord.ui.button(label='Overview', style=discord.ButtonStyle.green, custom_id='NavOver')
    async def over(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            await inter.response.send_modal(Editpage1(char=self.char,doer=inter.user.id))
    
    @discord.ui.button(label='Chrt (a)', style=discord.ButtonStyle.green, custom_id='NavCa')
    async def chrt_a(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            await inter.response.send_modal(Editpage2(char=self.char,doer=inter.user.id))
    
    @discord.ui.button(label='Chrt (b)', style=discord.ButtonStyle.green, custom_id='NavCb')
    async def chrt_b(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            await inter.response.send_modal(Editpage3(char=self.char,doer=inter.user.id))
    
    @discord.ui.button(label='Chrt (c)', style=discord.ButtonStyle.green, custom_id='NavCc')
    async def chrt_c(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            await inter.response.send_modal(Editpage4(char=self.char,doer=inter.user.id))

    @discord.ui.button(label='Conditions', style=discord.ButtonStyle.green, custom_id='NavCons')
    async def cons(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            await inter.response.send_modal(Editpage5(char=self.char,doer=inter.user.id))
    
    @discord.ui.button(label='All', style=discord.ButtonStyle.green, custom_id='NavAll')
    async def all_(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            await inter.response.send_modal(Editpage1(char=self.char,doer=inter.user.id,flow=True))

class VisibEmbed():
    def embed(char):
        emb = discord.Embed(title=f"Character Visibility Menu | {char['name']}",color=discord.Color.from_str('#ffdd70'))
        emb.add_field(name='● Private:', value="Only the user who created it can view it (cannot be used for rolls, since GM and admins can't see the stats)",inline=False)
        emb.add_field(name='● Server Specific:', value='Only the users of the server the user whitelist can view and by default the user of the server in which character was made can view the character',inline=False)
        emb.add_field(name='● Add Whitelist:', value='Extension of server only (server only must be active), but users can choose which servers can view the character by using this command in that server',inline=False)
        emb.add_field(name='● Remove Whitelist:', value='Extension of server only (server only must be active), users can remove the servers that they had previously whitelisted by using this command in that server',inline=False)
        emb.add_field(name='● Public:', value='Anyone can view the character',inline=False)
        return emb

class VisibSelectBar(ui.View):
    def __init__(self,char,user):
        super().__init__()
        self.embed = VisibEmbed.embed(char)
        self.char = char
        self.user = user
    
    @discord.ui.button(label='Private', style=discord.ButtonStyle.red, custom_id='VisPriv')
    async def over(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            self.char['visib'] = 2
            await inter.response.send_message(f"Character: {self.char['name']} | Visibility is now set to `Private`")
    
    @discord.ui.button(label='Server Specific', style=discord.ButtonStyle.green, custom_id='VisWhit')
    async def chrt_a(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            self.char['visib'] = 1
            self.char['whitelist'].append(inter.guild.id)
            await inter.response.send_message(f"Character: {self.char['name']} | Visibility is now set to `Server Specific`")
    
    @discord.ui.button(label='Add Whitelist', style=discord.ButtonStyle.green, custom_id='VisAdd')
    async def chrt_b(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            if inter.guild.id not in self.char['whitelist']:
                self.char['whitelist'].append(inter.guild.id)
                await inter.response.send_message(f"Character: {self.char['name']} | {inter.guild.name} added to whitelist")
            else:
                await inter.response.send_message(f"Character: {self.char['name']} | {inter.guild.name} is already in the whitelist")

    
    @discord.ui.button(label='Remove Whitelist', style=discord.ButtonStyle.green, custom_id='VisRem')
    async def chrt_c(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            try:
                self.char['whitelist'].remove(inter.guild.id)
                await inter.response.send_message(f"Character: {self.char['name']} | {inter.guild.name} removed from whitelist")
            except:
                await inter.response.send_message(f"Character: {self.char['name']} | {inter.guild.name} is not in the whitelist")


    @discord.ui.button(label='Public', style=discord.ButtonStyle.green, custom_id='VisPub')
    async def cons(self, inter:discord.Interaction, button:ui.Button):
        if inter.user.id==self.user.id:
            self.char['visib'] = 0
            await inter.response.send_message(f"Character: {self.char['name']} | Visibility is now set to `Public`")
    
#-------------------------------------------------------------
# Character Management Functions
#-------------------------------------------------------------


CharGroup = app_commands.Group(name="char", description="Character management suite")

@app_commands.command(name='create',description='Create your character!')
async def create(interaction: discord.Interaction):
    if aclient.canDo(interaction.user,'Create'):
        await interaction.response.send_modal(page1(interaction.user))
    else:
        await interaction.response.send_message("You aren't allowed to create character sheets, contact an admin if you think this is an error")

@app_commands.command(name='edit',description='Edit your characters')
async def edit(interaction: discord.Interaction):
    user = interaction.user
    if user.id in db['user_db']:
        char_list = db['user_db'][user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='Character Menu',options=options,custom_id='EditMenu')
        view.add_item(menu)
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                if aclient.canDo(interaction.user,'Edit',char_list[char_id]):
                    select_view = EditSelectBar(char_list[char_id],sub_inter.user)
                    await sub_inter.response.send_message(view=select_view,embed=select_view.embed)
                else:
                    await sub_inter.response.send_message("You are not allowed to edit characters of this server")
                    return
        menu.callback=internal_check
        await interaction.response.send_message(view=view)
    else:
        await interaction.response.send_message('User has no characters to display')

@app_commands.command(name='image', description='Add image to your character(s)')
async def image(interaction: discord.Interaction, attachment:discord.Attachment):
    if interaction.user.id in db['user_db']:
        char_list = db['user_db'][interaction.user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='Character Menu',options=options,custom_id='ImageMenu')
        view.add_item(menu)
        embed = discord.Embed(title='Character Image',color=discord.Color.from_str('#ffdd70'))
        embed.set_image(url=attachment.url)
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                embed.set_footer(text='Image added successfully!')
                view.stop()
                await sub_inter.message.edit(embed=embed,view=None)
                await sub_inter.response.send_message('Image added successfully!',ephemeral=True)
                db['user_db'][interaction.user.id]['char_list'][char_id]['img_url'] = attachment.url
        menu.callback=internal_check
        await interaction.response.send_message(embed=embed,view=view)
    else:
        await interaction.response.send_message('Create a character before adding an image!')

@app_commands.command(name='view', description='View your characters!')
async def view(interaction: discord.Interaction, user:discord.User):
    if user.id in db['user_db']:
        char_list = db['user_db'][user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='Character Menu',options=options,custom_id='ViewMenu')
        view.add_item(menu)
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                print(menu.values[0])
                char_id = int(menu.values[0])
                type(char_id)
                emb = ViewEmbed(char=char_list[char_id],user=interaction.user,char_id=char_id)
                await sub_inter.response.send_message(view=ViewNavBar(1,emb),embed=emb.page1())
        menu.callback=internal_check
        await interaction.response.send_message(view=view)
    else:
        await interaction.response.send_message('User has no characters to display')

@app_commands.command(name='set', description='Set an active character')
async def set_(interaction:discord.Interaction):
    if interaction.user.id in db['user_db']:
        char_list = db['user_db'][interaction.user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            # do visib == 2 make them private again
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        embed = discord.Embed(title=f'Active Character | {interaction.user.name}',description=f"Current active character set to: `{char_list[0]['name']}`")
        embed.set_thumbnail(url=char_list[0]['img_url'])
        menu=discord.ui.Select(placeholder='Character Menu',options=options,custom_id='ImageMenu')
        view.add_item(menu)
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                view.stop()
                char_list[char_id],char_list[0]=char_list[0],char_list[char_id]
                embed = discord.Embed(title=f'Active Character | {interaction.user.name}',description=f"Current active character set to: `{char_list[0]['name']}`")
                embed.set_thumbnail(url=char_list[0]['img_url'])
                await sub_inter.message.edit(embed=embed,view=None)
        menu.callback=internal_check
        await interaction.response.send_message(embed=embed,view=view)
    else:
        await interaction.response.send_message('Create a character before setting one as active')

@app_commands.command(name='visibility', description='Make your character private or public!')
async def visib(interaction:discord.Interaction):
    user = interaction.user
    if user.id in db['user_db']:
        char_list = db['user_db'][user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='Character Menu',options=options,custom_id='VisibMenu')
        view.add_item(menu)
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                emb = ViewEmbed(char=char_list[char_id],user=interaction.user,char_id=char_id)
                select_view = VisibSelectBar(char_list[char_id],sub_inter.user)
                await sub_inter.response.send_message(view=select_view,embed=select_view.embed)
        menu.callback=internal_check
        await interaction.response.send_message(view=view)
    else:
        await interaction.response.send_message('User has no characters to display')

@app_commands.command(name='delete', description='Delete your character sheet')
async def delete(interaction:discord.Interaction):
    if interaction.user.id in db['user_db']:
        char_list = db['user_db'][interaction.user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='Character Menu',options=options,custom_id='DeleteMenu')
        view.add_item(menu)
        embed = discord.Embed(title='Character Deletion',color=discord.Color.from_str('#ffdd70'))
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                if not aclient.canDo(interaction.user,'Delete',db['user_db'][interaction.user.id]['char_list'][char_id]):
                    embed.set_footer(text='Unable to delete character [Permission Denied]')
                    await sub_inter.message.edit(embed=embed,view=None)
                    await sub_inter.response.send_message('Unable to delete character [Permission Denied]',ephemeral=True)
                    view.stop()
                    return
                embed.set_footer(text='Character deleted successfully!')
                view.stop()
                db['user_db'][interaction.user.id]['char_list'].pop(char_id)
                await sub_inter.message.edit(embed=embed,view=None)
                await sub_inter.response.send_message('Character deleted successfully!',ephemeral=True)
        menu.callback=internal_check
        await interaction.response.send_message(embed=embed,view=view)
    else:
        await interaction.response.send_message('Create a character before deleting one!')

CharGroup.add_command(create)
CharGroup.add_command(edit)
CharGroup.add_command(image)
CharGroup.add_command(view)
#CharGroup.add_command(visib)
CharGroup.add_command(set_)
CharGroup.add_command(delete)
bot.add_command(CharGroup)

#-------------------------------------------------------------
# Admin control commands
#-------------------------------------------------------------

AdminGroup = app_commands.Group(name="admin", description="Admin Control Panel")

def is_admin():
    def predicate(interaction:discord.Interaction):
        roles = [role.id for role in interaction.user.roles]
        if interaction.user.guild_permissions.administrator:
            return True
        elif db['server_db'][interaction.guild.id]['admin'] in roles:
            return True
        else:
            return False
    return app_commands.check(predicate)

@app_commands.command(name='create', description='Create characters for your players')
@is_admin()
async def adminCreate(interaction:discord.Interaction,user:discord.User):
    if aclient.canDo(interaction.user,'Create'):
        await interaction.response.send_modal(page1(user))
    else:
        await interaction.response.send_message("You aren't allowed to create character sheets for this user, contact the developer if you think this is an error")

@app_commands.command(name='edit', description='Edit characters for your players')
@is_admin()
async def adminEdit(interaction:discord.Interaction,user:discord.User):
    if user.id in db['user_db']:
        char_list = db['user_db'][user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='Admin Panel | Character Menu',options=options,custom_id='AdminEditMenu')
        view.add_item(menu)
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                if aclient.canDo(interaction.user,'Edit',char_list[char_id]):
                    select_view = EditSelectBar(char_list[char_id],sub_inter.user)
                    await sub_inter.response.send_message(view=select_view,embed=select_view.embed)
                else:
                    await interaction.response.send_message("Unable to edit character [Permission Denied]")
        menu.callback=internal_check
        await interaction.response.send_message(view=view)
    else:
        await interaction.response.send_message('User has no characters to display')

@app_commands.command(name='delete', description='Delete characters of your players')
@is_admin()
async def adminDelete(interaction:discord.Interaction,user:discord.User):
    if user.id in db['user_db']:
        char_list = db['user_db'][user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='Character Menu',options=options,custom_id='AdminViewMenu')
        view.add_item(menu)
        embed = discord.Embed(title='Admin Panel | Character Deletion',color=discord.Color.from_str('#ffdd70'))
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                if not aclient.canDo(interaction.user,'Delete',db['user_db'][user.id]['char_list'][char_id]):
                    embed.set_footer(text='Unable to delete character [Permission Denied]')
                    await sub_inter.message.edit(embed=embed,view=None)
                    await sub_inter.response.send_message('Unable to delete character [Permission Denied]',ephemeral=True)
                char_list.pop(char_id)
                if len(char_list)==0:
                    db['user_db'].pop(user.id)
                embed.set_footer(text='Character deleted successfully!')
                await sub_inter.message.edit(embed=embed,view=None)
                await sub_inter.response.send_message('Character deleted successfully!',ephemeral=True)
                view.stop()
        menu.callback=internal_check
        await interaction.response.send_message(view=view)
    else:
        await interaction.response.send_message('User has no characters to delete')



@app_commands.command(name='image', description='Add image to your character(s)')
@is_admin()
async def adminImage(interaction: discord.Interaction, member:discord.Member,attachment:discord.Attachment):
    if member.id in db['user_db']:
        char_list = db['user_db'][member.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='Character Menu',options=options,custom_id='ImageMenu')
        view.add_item(menu)
        embed = discord.Embed(title='Character Image',color=discord.Color.from_str('#ffdd70'))
        embed.set_image(url=attachment.url)
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                embed.set_footer(text='Image added successfully!')
                view.stop()
                await sub_inter.message.edit(embed=embed,view=None)
                await sub_inter.response.send_message('Image added successfully!',ephemeral=True)
                db['user_db'][member.id]['char_list'][char_id]['img_url'] = attachment.url
        menu.callback=internal_check
        await interaction.response.send_message(embed=embed,view=view)
    else:
        await interaction.response.send_message('Create a character before adding an image!')

@AdminGroup.error
async def on_error(interaction:discord.Interaction,error:discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message('You are not an admin!', ephemeral=True)
    else:
        await interaction.response.send_message(error)

AdminGroup.add_command(adminCreate)
AdminGroup.add_command(adminEdit)
AdminGroup.add_command(adminDelete)
AdminGroup.add_command(adminImage)
bot.add_command(AdminGroup)


#-------------------------------------------------------------
# Server Config commands functions
#-------------------------------------------------------------

ConfigGroup = app_commands.Group(name="config", description="Server Config Panel")
IntConfigGroup = app_commands.Group(name="allow", description="Server Config Panel")

@app_commands.command(name='admin',description='Use this to set a role as admin role in the bot')
@app_commands.describe(role='Admin role')
@is_admin()
async def adminRole(interaction:discord.Interaction, role:discord.Role):
    db['server_db'][interaction.guild.id]['admin'] = role.id
    await interaction.response.send_message(f"Users with the role `{role}` can now use /admin commands")

@app_commands.command(name='gm',description='Use this to set a role as gm role in the bot')
@app_commands.describe(role='GM role')
@is_admin()
async def gmRole(interaction:discord.Interaction, role:discord.Role):
    db['server_db'][interaction.guild.id]['gm'] = role.id
    await interaction.response.send_message(f"Users with the role `{role}` can now use /gm commands")

@app_commands.command(name='external',description='Allow/Restrict characters which were not made in this server')
@app_commands.describe(setting='True: Allow characters, False: Restrict Characters')
@is_admin()
async def configRestrict(interaction:discord.Interaction, setting:bool):
    if setting:
        db['server_db'][interaction.guild.id]['toUse'] = True
    else:
        db['server_db'][interaction.guild.id]['toUse'] = False
    await interaction.response.send_message(f"Server configuration for `Allow External Characters` for all players is now set to `{setting}`")

@app_commands.command(name='create',description='Allow/Restrict character creation')
@app_commands.describe(setting='True: Allow creation, False: Disallow creation')
@is_admin()
async def configCreate(interaction:discord.Interaction, setting:bool):
    if setting:
        db['server_db'][interaction.guild.id]['toCreate'] = True
    else:
        db['server_db'][interaction.guild.id]['toCreate'] = False
    await interaction.response.send_message(f"Server configuration for `Character Creation` for all players is now set to `{setting}`")

@app_commands.command(name='edit',description='Allow/Restrict character edits')
@app_commands.describe(setting='True: Allow edits, False: Disallow edits')
@is_admin()
async def configEdit(interaction:discord.Interaction, setting:bool):
    if setting:
        db['server_db'][interaction.guild.id]['toEdit'] = True
    else:
        db['server_db'][interaction.guild.id]['toEdit'] = False
    await interaction.response.send_message(f"Server configuration for `Character Edits` for all players is now set to `{setting}`")

@app_commands.command(name='delete',description='Allow/Restrict character deletion')
@app_commands.describe(setting='True: Allow edits, False: Disallow edits')
@is_admin()
async def configDelete(interaction:discord.Interaction, setting:bool):
    if setting:
        db['server_db'][interaction.guild.id]['toDelete'] = True
    else:
        db['server_db'][interaction.guild.id]['toDelete'] = False
    await interaction.response.send_message(f"Server configuration for `Character Deletion` for all players is now set to `{setting}`")

class rulesButton(ui.View):
    def __init__(self, char):
        super().__init__()


@app_commands.command(name='system',description='Choose which sort of roll mechanic you want to use')
@is_admin()
async def gameSystem(interaction:discord.Interaction):
    view=discord.ui.View()
    options = [
        discord.SelectOption(label="System 1",value="System 1"),
        discord.SelectOption(label="System 2",value="System 2"),
        discord.SelectOption(label="System 3",value="System 3"),
    ]
    menu=discord.ui.Select(placeholder='Mechanics Menu',options=options,custom_id='MechanicMenu')
    view.add_item(menu)
    async def internal_check(sub_inter:discord.Interaction):
        if sub_inter.user.id == interaction.user.id:
            view.stop()
            embed = discord.Embed(title=f'Game System | {interaction.user.name}',color=discord.Color.from_str('#ffdd70'))
            embed.description = f"{menu.values[0]} has been set as current server's ruleset"
            db['server_db'][interaction.guild.id]['ruleSet'] = menu.values[0]
            await sub_inter.message.edit(embed=embed,view=None)
    menu.callback= internal_check
    embed = discord.Embed(title=f'Game System | {interaction.user.name}',color=discord.Color.from_str('#ffdd70'))
    embed.description = f"""
Game system selectors allows you to choose which rules to use while rolling the dice
The following systems are currently supported by the bot:
• System 1
• System 2
• System 3
~~**⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃⁃**~~
‣**System 1:**
> Rogue Trader/Deathwatch

**System 2:**
> War/Black Crusade

**System 3:**
> Dark Heresy 2nd Edition
`Current rule-set is: {db['server_db'][interaction.guild.id]['ruleSet']}`
Press `rules` to see how the the rules used in the bot
"""
    rules = discord.ui.Button(label='Rules',style=discord.ButtonStyle.red, custom_id='ConfigRules')
    async def button_check(sub_inter:discord.Interaction):
         if sub_inter.user.id == interaction.user.id:
            view.stop()
            embed = discord.Embed(title=f'Game System | {interaction.user.name}',color=discord.Color.from_str('#ffdd70'))
            embed.description = f"""**System 1: Rogue Trader/Deathwatch**
- Oldest system.
- Gains DoS/F for every 10 points a characteristic was exceeded/failed, meaning you can pass/fail a test with 0 DoS/F (if I understand it correctly.)

**System 2: Only War/Black Crusade**
- Newer system (but not the newest)
- Simplest
- Passing/failing the test grants 1 DoS/F. For every 10 points more the test is passed/failed, you gain another DoS/F.
- Always has at least 1 DoS or DoF.

**System 3: Dark Heresy 2nd Edition**
- Newest System
- Like System 2, passing/failing grants 1 Dos/F. However, additional DoS/F is calculated differently.
- Additional DoS are gained equal to the 10s digit of the target value minus the 10s digit of the roll. (TARGET VALUE - ROLL)
- Additional DoF are gained equal to the 10s digit of the roll minus the 10s digit of the target value. (ROLL - TARGET VALUE)"""
            await sub_inter.message.edit(embed=embed,view=None)
    rules.callback=button_check
    view.add_item(rules)
    await interaction.response.send_message(embed=embed,view=view)
    
    

IntConfigGroup.add_command(configCreate)
IntConfigGroup.add_command(configEdit)
IntConfigGroup.add_command(configDelete)
ConfigGroup.add_command(gameSystem)
ConfigGroup.add_command(adminRole)
ConfigGroup.add_command(gmRole)
ConfigGroup.add_command(IntConfigGroup)
bot.add_command(ConfigGroup)

#-------------------------------------------------------------
# GM commands functions
#-------------------------------------------------------------

GmGroup = app_commands.Group(name="gm", description="GM Panel")
ExpGroup = app_commands.Group(name="exp", description="Exp Panel")

def is_gm():
    def predicate(interaction:discord.Interaction):
        roles = [role.id for role in interaction.user.roles]
        if interaction.user.guild_permissions.administrator:
            return True
        elif db['server_db'][interaction.guild.id]['admin'] in roles:
            return True
        elif db['server_db'][interaction.guild.id]['gm'] in roles:
            return True
        else:
            return False
    return app_commands.check(predicate)

@app_commands.command(name='create', description='Create characters for your players')
@is_gm()
async def gmCreate(interaction:discord.Interaction,user:discord.User):
    if aclient.canDo(interaction.user,'Create'):
        await interaction.response.send_modal(page1(user))
    else:
        await interaction.response.send_message("You aren't allowed to create character sheets for this user, contact the developer if you think this is an error")

@app_commands.command(name='edit', description='Edit characters for your players')
@is_gm()
async def gmEdit(interaction:discord.Interaction,user:discord.User):
    if user.id in db['user_db']:
        char_list = db['user_db'][user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='GM Panel | Character Menu',options=options,custom_id='gmEditMenu')
        view.add_item(menu)
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                if aclient.canDo(interaction.user,'Edit',char_list[char_id]):
                    select_view = EditSelectBar(char_list[char_id],sub_inter.user)
                    await sub_inter.response.send_message(view=select_view,embed=select_view.embed)
                else:
                    await interaction.response.send_message("Unable to edit character [Permission Denied]")
        menu.callback=internal_check
        await interaction.response.send_message(view=view)
    else:
        await interaction.response.send_message('User has no characters to display')

@app_commands.command(name='set', description='Set expirience of characters for your players')
@app_commands.describe(user='The user whose character exp you wish to set', amount='The amount of exp you want to set it')
@is_gm()
async def gmExpSet(interaction:discord.Interaction,user:discord.User,amount:int):
    if user.id in db['user_db']:
        char_list = db['user_db'][user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='GM Panel | Character Menu',options=options,custom_id='gmExpMenu')
        view.add_item(menu)
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                if aclient.canDo(interaction.user,'Edit',char_list[char_id]):
                    char_list[char_id]['exp']=amount
                    await sub_inter.response.send_message(f"{char_list[char_id]['name']}'s exp is set to {amount}")
                else:
                    await interaction.response.send_message("Unable to edit character [Permission Denied]")
        menu.callback=internal_check
        await interaction.response.send_message(view=view)
    else:
        await interaction.response.send_message('User has no characters to display')

@app_commands.command(name='add', description='Set expirience of characters for your players')
@app_commands.describe(user='The user whose character exp you wish to set', amount='(use - to subtract) The amount of exp you want to add/subtract to the current exp')
@is_gm()
async def gmExpAdd(interaction:discord.Interaction,user:discord.User,amount:int):
    if user.id in db['user_db']:
        char_list = db['user_db'][user.id]['char_list']
        options = []
        view=discord.ui.View()
        roles = [role.id for role in interaction.user.roles]
        for char in range(len(char_list)):
            if char_list[char]['visib'] != 2:
                if interaction.user.guild_permissions.administrator:
                    pass
                elif char_list[char]['owner'] == interaction.user.id:
                    pass
                elif db['server_db'][interaction.guild.id]['admin'] in roles:
                    pass
                elif db['server_db'][interaction.guild.id]['gm'] in roles:
                    pass
                else:
                    continue
            options.append(discord.SelectOption(label=char_list[char]['name'],value=char))
        if not options:
            await interaction.response.send_message('No Viewable Characters available')
            return
        menu=discord.ui.Select(placeholder='GM Panel | Character Menu',options=options,custom_id='gmExpMenu')
        view.add_item(menu)
        async def internal_check(sub_inter:discord.Interaction):
            if sub_inter.user.id == interaction.user.id:
                char_id = int(menu.values[0])
                if aclient.canDo(interaction.user,'Edit',char_list[char_id]):
                    char_list[char_id]['exp']+=amount
                    await sub_inter.response.send_message(f"{char_list[char_id]['name']}'s exp is set to {amount}")
                else:
                    await interaction.response.send_message("Unable to edit character [Permission Denied]")
        menu.callback=internal_check
        await interaction.response.send_message(view=view)
    else:
        await interaction.response.send_message('User has no characters to display')

GmGroup.add_command(gmCreate)
GmGroup.add_command(gmEdit)
ExpGroup.add_command(gmExpSet)
ExpGroup.add_command(gmExpAdd)
GmGroup.add_command(ExpGroup)
bot.add_command(GmGroup)

#-------------------------------------------------------------
# Rolling commands classes
#-------------------------------------------------------------

class AddPlayer(ui.Modal, title = "Character Sheet | Overview"):
    def __init__(self,_id,msg,view):
        super().__init__()
        self.id = _id
        self.msg=msg
        self.view=view
    answer1= ui.TextInput(label="● Name:", style=discord.TextStyle.short, placeholder="What is the Character's Name?")
    answer2= ui.TextInput(label="● Characteristics (Name):", style=discord.TextStyle.short, placeholder='What is the name of the characteristics?')
    answerag= ui.TextInput(label="● Agility (for tiebreakers) (Value):", style=discord.TextStyle.short, placeholder='What is the name of the characteristics?')
    answer3= ui.TextInput(label="● Characteristics Bonus(Value):", default=0,style=discord.TextStyle.short, max_length=2, placeholder='What is the value of the characteristics bonus?')
    answer4= ui.TextInput(label="● No.of Rolls:", style=discord.TextStyle.short, default=1,max_length=1, placeholder='How many rolls should the bot do?')


    async def on_submit(self, interaction: discord.Interaction):
        char = {}
        char['owner'] = f"{self.answer1} | <@{interaction.user.id}>"
        char['name'] = str(self.answer1)
        char['used_chrt'] = str(self.answer2)
        char['bonus'] = int(str(self.answer3))
        char['rolled'] = 0
        char['ag'] = int(str(self.answerag))
        for i in range(int(str(self.answer4))):
            rolled = random.randint(1,10)
            bonus=char['bonus']
            if rolled+bonus>char['rolled']:
                    char['rolled']=rolled
                    char['bonus'] = bonus
                    char['total'] = rolled+bonus
        db['int_ids'][self.id]['values'].append(char)
        db["int_ids"][self.id]['values'] = sorted(db["int_ids"][self.id]['values'], key=lambda i: (i['total']))
        db["int_ids"][self.id]['values'].reverse()
        db["int_ids"][self.id]['npcs'].append(char)
        await interaction.response.send_message('Added!', ephemeral=True)
        await self.msg.edit(embed=self.view.embed.embed(self.id))

class RemPlayer(ui.Modal, title = "Character Sheet | Overview"):
    def __init__(self,_id,msg,view):
        super().__init__()
        self.id = _id
        self.msg=msg
        self.view=view
    answer1= ui.TextInput(label="● Number:", style=discord.TextStyle.short, placeholder="What is the rank/order of the player you wish to remove?")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            copy = db['int_ids'][self.id]['values'][int(str(self.answer1))-1].copy()
            db['int_ids'][self.id]['values'].pop(int(str(self.answer1))-1)
            await interaction.response.send_message(f'''{interaction.user} removed a character `{copy['name']}` of <@{copy['owner']}> ''')
            await self.msg.edit(embed=self.view.embed.embed(self.id))
        except:
            await interaction.response.send_message('Invalid Rank',ephemeral=True)

class intRollEmbed():
    def embed(self,_id=None) -> discord.Embed:
        desc=''
        if _id:
            for i in range(len(db['int_ids'][_id]['values'])):
                desc=desc+f"**{i+1}. {f'''<@{db['int_ids'][_id]['values'][i]['owner']}''' if '|' not in str(db['int_ids'][_id]['values'][i]['owner']) else db['int_ids'][_id]['values'][i]['owner']}>**\n> Name: {db['int_ids'][_id]['values'][i]['name']}\n> Characteristics: {db['int_ids'][_id]['values'][i]['used_chrt']}\n> Rolled: {db['int_ids'][_id]['values'][i]['rolled']}\n> Bonus: {db['int_ids'][_id]['values'][i]['bonus']}\n> Total: {db['int_ids'][_id]['values'][i]['rolled']+db['int_ids'][_id]['values'][i]['bonus']}\n"
            emb = discord.Embed(title = f"Initiative d10 Roll | {len(db['int_ids'][_id]['values']) if db['int_ids'][_id]['values'] else 0} Player(s)", description=desc,color=discord.Color.from_str('#ffdd70'))
        else:
            desc = '\n*No Players to display the order* \\*Cricket Noises*'
            emb = discord.Embed(title = f"Initiative d10 Roll | 0 Player(s)", description=desc,color=discord.Color.from_str('#ffdd70'))
        return emb

class intRollView(ui.View):
    def __init__(self,timeout=None):
        super().__init__(timeout=timeout)
        self.embed = intRollEmbed()

    @discord.ui.select(placeholder="Select your active character's characteristic",options=[discord.SelectOption(label=int_abv[opt],value=opt) for opt in int_abv],custom_id='InitiativeViewMenu',min_values=1,max_values=2)
    async def rollMenu(self, sub_inter:discord.Interaction, menu:ui.Select):
        if sub_inter.user.id in db['int_ids'][sub_inter.message.id]['players']:
            await sub_inter.response.send_message('You can only roll once!',ephemeral=True)
            return
        if sub_inter.user.id in db['user_db']:
            char = db['user_db'][sub_inter.user.id]['char_list'][0].copy()
            # if char['visib'] != 2:
            #     await sub_inter.response.send_message('Character sheet visibility is `Private`, Change the visibility of your character sheet using `/char visibility` or use a different character using `/char set`',ephemeral=True)
            #     return
            # elif char['visib'] == 1:
            #     if not sub_inter.guild.id in char['whitelist']:
            #         await sub_inter.response.send_message('Character sheet visibility is `Server Specific`, whitelist this server or change the visibility of your character sheet using `/char visibility` or use a different character using `/char set`',ephemeral=True)
            #         return
            char['rolled']=0
            for chrt in menu.values:
                rolled = random.randint(1,10)
                if chrt=='const':
                    bonus=0
                else:
                    bonus=int(int(char[chrt])/10)+int(char['u'+chrt])
                if rolled+bonus>char['rolled']:
                    char['rolled']=rolled
                    char['used_chrt']=int_abv[chrt]
                    char['bonus'] = bonus
                    char['total'] = rolled+bonus
            db["int_ids"][sub_inter.message.id]['values'].append(char)
            db["int_ids"][sub_inter.message.id]['values'] = sorted(db["int_ids"][sub_inter.message.id]['values'], key=lambda i: (i['total']))
            db["int_ids"][sub_inter.message.id]['values'].reverse()
            db['int_ids'][sub_inter.message.id]['players'].append(sub_inter.user.id)
            await sub_inter.response.edit_message(embed=self.embed.embed(_id=sub_inter.message.id))
        else:
            await sub_inter.response.send_message('You have no characters',ephemeral=True)

    @discord.ui.button(label='Add NPC', style=discord.ButtonStyle.green, custom_id='AddPlay')
    async def rollAdd(self, inter:discord.Interaction, button:ui.Button):
        await inter.response.send_modal(AddPlayer(inter.message.id,inter.message,self))


    @discord.ui.button(label='Remove Character', style=discord.ButtonStyle.red, custom_id='RemPlay')
    async def rollRem(self, inter:discord.Interaction, button:ui.Button):
        await inter.response.send_modal(RemPlayer(inter.message.id,inter.message,self))
    
    @discord.ui.button(label='Reroll', style=discord.ButtonStyle.green, custom_id='ReRoll')
    async def reRoll(self, inter:discord.Interaction, button:ui.Button):
        roles = [role.id for role in inter.user.roles]
        if inter.user.guild_permissions.administrator:
            pass
        elif db['server_db'][inter.guild.id]['admin'] in roles:
            pass
        elif db['server_db'][inter.guild.id]['gm'] in roles:
            pass
        else:
            await inter.response.send_message('Error: You are not a gm or an admin to do this action')
            return
        db['int_ids'][inter.id]=db['int_ids'][inter.message.id].copy()
        for npc in db['int_ids'][inter.id]['values']:
            npc['rolled'] = 0
            rolled = random.randint(1,10)
            bonus=npc['bonus']
            if rolled+bonus>npc['rolled']:
                    npc['rolled']=rolled
                    npc['bonus'] = bonus
                    npc['total'] = rolled+bonus
        db["int_ids"][inter.id]['values'] = sorted(db["int_ids"][inter.id]['values'], key=lambda i: (i['total']))
        db["int_ids"][inter.id]['values'].reverse()
        await inter.response.send_message(view=intRollView(timeout=None),embed=self.embed.embed(_id=inter.id))
        message = await inter.original_response()
        await inter.message.edit(view=None)
        db['int_ids'][message.id] = db["int_ids"][inter.id]
        db["int_ids"].pop(inter.id)

    @discord.ui.button(label='Repost', style=discord.ButtonStyle.green, custom_id='RePost')
    async def rePost(self, inter:discord.Interaction, button:ui.Button):
        roles = [role.id for role in inter.user.roles]
        if inter.user.guild_permissions.administrator:
            pass
        elif db['server_db'][inter.guild.id]['admin'] in roles:
            pass
        elif db['server_db'][inter.guild.id]['gm'] in roles:
            pass
        else:
            await inter.response.send_message('Error: You are not a gm or an admin to do this action')
            return
        await inter.response.send_message(view=self,embed=self.embed.embed(inter.message.id))
        message = await inter.original_response()
        db['int_ids'][message.id] = db['int_ids'][inter.message.id]
        await inter.message.edit(view=None)
#-------------------------------------------------------------
# Rolling commands functions
#-------------------------------------------------------------

Rollgroup = app_commands.Group(name="roll", description="Roll the dice for whatever reason you want")

def get_degree_of_task(target,rolled,system):
    if rolled>target:
        target,rolled=rolled,target
    if system=="System 1":
        return (target-rolled)//10
    elif system=="System 2":
        return 1+(target-rolled)//10
    elif system=="System 3":
        return 1+(target//10-rolled//10)
    return 0

@app_commands.command(name='char',description="Roll a d100 with (or without) your character's modifiers")
@app_commands.describe(syntax='Format: {shorthand of characteristics/ a base value} {extra modifiers}')
async def roll(interaction:discord.Interaction, syntax:str):
    if syntax.count(' ')>=1:
        base_modifier,extra_modifiers = syntax.split(' ',maxsplit=1)
    else:
        base_modifier = syntax
        extra_modifiers = 0
    character=0
    if base_modifier.isalpha():
        if interaction.user.id in db['user_db']:
            if base_modifier.lower() in db['user_db'][interaction.user.id]['char_list'][character]:
                emb_title = db['user_db'][interaction.user.id]['char_list'][character]['name']
                base_title='Characteristic'
                base_name='Characteristic Value:'
                unnat_base = int(db['user_db'][interaction.user.id]['char_list'][character]['u'+base_modifier.lower()])
                base = int(db['user_db'][interaction.user.id]['char_list'][character][base_modifier.lower()])
                base_full = abv[base_modifier.lower()]
            else:
                await interaction.response.send_message('Invalid characteristic modifier referenced, please use the valid short hand',ephemeral=True)
                return
        else:
            await interaction.response.send_message('You need to have a character to reference its stats',ephemeral=True)
            return
    elif base_modifier.isalnum():
        try:
            base = int(base_modifier)
            unnat_base = 0
            emb_title = 'Void'
            base_title='Base'
            base_name='Base Modifier:'
            base_full = base_modifier
        except:
            await interaction.response.send_message("Please use only numbers or your character's characteristics",ephemeral=True)
            return
    else:
        await interaction.response.send_message("Please use only numbers or your character's characteristics",ephemeral=True)
        return
    if extra_modifiers:
        try:
            tree = ast.parse(extra_modifiers, mode='eval')
        except SyntaxError:
            em = 0
        if not all(isinstance(node, (ast.Expression,
                ast.UnaryOp, ast.unaryop,
                ast.BinOp, ast.operator,
                ast.Constant)) for node in ast.walk(tree)):
            em = 0
        em = eval(compile(tree, filename='', mode='eval'))
    else:
        em=0
    if em > 60:
        em = 60
    elif em < -60:
        em = -60
    acc = base+em
    rolled = random.randint(1,100)
    if rolled <= acc :
        emb = discord.Embed(title=f"Rolling | {emb_title} | {base_title}: {base_full}",color=discord.Color.from_rgb(0,255,111))
        emb.add_field(name=base_name,value=base)
        emb.add_field(name='Additional Modifier(s):',value=em)
        emb.add_field(name='Target Number:',value=acc)
        if int(acc/10)-int(rolled/10)>0:
            emb.add_field(name='Degree of Success:', value=get_degree_of_task(acc,rolled,db['server_db'][interaction.guild.id]['ruleSet'])+unnat_base)
        else:
            emb.add_field(name='Degree of Success:', value=get_degree_of_task(acc,rolled,db['server_db'][interaction.guild.id]['ruleSet'])+unnat_base)
        emb.add_field(name='Rolled:',value=rolled)
        await interaction.response.send_message(embed=emb)
    else:
        emb = discord.Embed(title=f"Rolling | {emb_title} | {base_title}: {base_full}",color=discord.Color.from_rgb(255,25,25))
        emb.add_field(name=base_name,value=base)
        emb.add_field(name='Additional Modifier(s):',value=em)
        emb.add_field(name='Target Number:',value=acc)
        if int(acc/10)-int(rolled/10)<0:
            emb.add_field(name='Degree of Failure:', value=get_degree_of_task(acc,rolled,db['server_db'][interaction.guild.id]['ruleSet']))
        else:
            emb.add_field(name='Degree of Failure:', value=get_degree_of_task(acc,rolled,db['server_db'][interaction.guild.id]['ruleSet']))
        emb.add_field(name='Rolled:',value=rolled)
        await interaction.response.send_message(embed=emb)


@app_commands.command(name='dmg', description="Roll a d10 with(out) modifiers for damage")
@app_commands.describe(syntax='Format: {name of weapon} {xd10+y [x:no.of rolls, y:modifiers]} {damage type} {penetration of weapon}',multi_shot='If the weapon is single shot (mods are added once) or multi shot weapon (mods added with each roll)')
async def dmg(interaction:discord.Interaction, syntax:str, multi_shot:bool=True):
    try:
        name,dice,dmg_type,pent = syntax.split(' ')
        rolls,side_mod=dice.split('d')
        if '+' in side_mod:
            sides,mods = side_mod.split('+')
        elif '-' in side_mod:
            sides,mods = side_mod.split('-')
        else:
            try:
                sides = int(side_mod)
                mods = 0
            except:
                raise ValueError()
        #sides = int(sides)
        mods = int(mods)
        sides = 10
        dmgs = {1:"<:1_:1024361155818434590>",2:"<:2_:1024361158188212224>",3:"<:3_:1024361160356663379>",4:"<:4_:1024361162747428924>",5:"<:5_:1024361165272404008>",6:"<:6_:1024361169819025418>",7:"<:7_:1024361172255907910>",8:"<:8_:1024361176659931187>",9:"<:9_:1024361178778050661>",10:"<:10:1024361544642994237>"}
        total_dmg = 0
        desc=''
        if multi_shot==True:
            for i in range(int(rolls)):
                dmg = random.randint(1,sides)
                total_dmg+= dmg+mods
                desc = desc+dmgs[dmg]
        else:
            for i in range(int(rolls)):
                dmg = random.randint(1,sides)
                total_dmg+= dmg
                desc = desc+dmgs[dmg]
            total_dmg+=mods
        
        emb = discord.Embed(title=f'Rolling | Weapon: {name}', color=discord.Color.from_str('#ffdd70'),description=f"**Rolls:**\n{desc}")
        abv = {'E' : "Energy",'I' : "Impact",'R' : "Rending",'X' : "Explosive"}
        emb.add_field(name='Total Damage:', value=total_dmg, inline=False)
        emb.add_field(name='Type:' ,value=abv[dmg_type.upper()])
        emb.add_field(name='Penetration:' ,value=pent)
        await interaction.response.send_message(embed=emb)

    except Exception as e:
        print(e)
        await interaction.response.send_message('Incorrect sytax, Ex: `Knife 1d10 R 5`', ephemeral=True)


@app_commands.command(name='psyc', description="Roll a d100 with(out) modifiers for psyc rolls")
@app_commands.describe(syntax='Format: {shorthand of characteristics/ a base value} {extra modifiers}')
async def psyc(interaction:discord.Interaction, syntax:str):
    if syntax.count(' ')>=1:
        base_modifier,extra_modifiers = syntax.split(' ',maxsplit=1)
    else:
        base_modifier = syntax
        extra_modifiers = 0
    character=0
    if base_modifier.isalpha():
        if interaction.user.id in db['user_db']:
            if base_modifier.lower() in db['user_db'][interaction.user.id]['char_list'][character] or base_modifier=='f':
                emb_title = db['user_db'][interaction.user.id]['char_list'][character]['name']
                base_title='Characteristic'
                base_name='Characteristic Value:'
                base = int(db['user_db'][interaction.user.id]['char_list'][character][base_modifier.lower()])
                base_full = abv[base_modifier.lower()]
            else:
                await interaction.response.send_message('Invalid characteristic modifier referenced, please use the valid short hand',ephemeral=True)
                return
        else:
            await interaction.response.send_message('You need to have a character to reference its stats',ephemeral=True)
            return
    elif base_modifier.isalnum():
        try:
            base = int(base_modifier)
            emb_title = 'Void'
            base_title='Base'
            base_name='Base Modifier:'
            base_full = base_modifier
        except:
            await interaction.response.send_message('Invalid characteristic modifier referenced, please use the valid short hand',ephemeral=True)
            return
    else:
        emb_title = 'Void'
        base_title='Base'
        base_name='Base Modifier:'
        base_full = base_modifier
        base = int(base_modifier)
    if extra_modifiers:
        try:
            tree = ast.parse(extra_modifiers, mode='eval')
        except SyntaxError:
            em = 0
        if not all(isinstance(node, (ast.Expression,
                ast.UnaryOp, ast.unaryop,
                ast.BinOp, ast.operator,
                ast.Num)) for node in ast.walk(tree)):
            em = 0
        em = eval(compile(tree, filename='', mode='eval'))
    else:
        em=0
    if base_modifier=='f':
        base = 100
    if em > 60:
        em = 60
    elif em < -60:
        em = -60
    acc = base+em
    
    rolled = random.randint(1,100)
    if rolled <= acc :
        emb = discord.Embed(title=f"Rolling | {emb_title} | {base_title}: {base_full}",color=discord.Color.from_rgb(0,255,111))
        emb.add_field(name=base_name,value=base)
        emb.add_field(name='Additional Modifier(s):',value=em)
        emb.add_field(name='Target Number:',value=acc)
        emb.add_field(name='Degree of Success:',value=get_degree_of_task(acc,rolled,db['server_db'][interaction.guild.id]['ruleSet']))
        emb.add_field(name='Rolled:',value=rolled)
        if str(rolled)==str(rolled)[::-1]:
            reroll = random.randint(1,100)
            tot =reroll
            if reroll>75:
                dubroll = 75
            else:
                dubroll= reroll
            out,val = dub_notes[dub[dubroll]].split(':',maxsplit=1)
            emb.add_field(name='Psychic Phenomena:',value=f'● **Re-Roll:**  {reroll}\n● **Total (without DoS):**  {tot}\n● **{out}:** {val}',inline=False)
            if reroll>75:
                reroll = random.randint(1,100)
                out,val = sev_five_notes[sev_five[reroll]].split(':',maxsplit=1)
                emb.add_field(name='Perils of the Warp:',value=f'● **Re-Roll:** {reroll}\n● **{out}:** {val}',inline=False)
        await interaction.response.send_message(embed=emb)
    else:
        emb = discord.Embed(title=f"Rolling | {emb_title} | {base_title}: {base_full}",color=discord.Color.from_rgb(255,25,25))
        emb.add_field(name=base_name,value=base)
        emb.add_field(name='Additional Modifier(s):',value=em)
        emb.add_field(name='Target Number:',value=acc)
        emb.add_field(name='Degree of Failure:',value=get_degree_of_task(acc,rolled,db['server_db'][interaction.guild.id]['ruleSet']))
        emb.add_field(name='Rolled:',value=rolled)
        if str(rolled)==str(rolled)[::-1] and str(rolled)>1:
            reroll = random.randint(1,100)
            tot = reroll+get_degree_of_task(acc,rolled,db['server_db'][interaction.guild.id]['ruleSet'])*10
            if reroll>75:
                dubroll = 75
            else:
                dubroll = reroll
            out,val = dub_notes[dub[dubroll]].split(':',maxsplit=1)
            emb.add_field(name='Psychic Phenomena:',value=f'● **Re-Roll:**  {reroll}\n● **Total (with DoF):**  {tot}\n● **{out}:** {val}',inline=False)
            if reroll>75:
                reroll = random.randint(1,100)
                out,val = sev_five_notes[sev_five[reroll]].split(':',maxsplit=1)
                emb.add_field(name='Perils of the Warp:',value=f'● **Re-Roll:** {reroll}\n● **{out}:** {val}',inline=False)
        await interaction.response.send_message(embed=emb)


@app_commands.command(name='initiative', description="Roll a d10 initiative roll for other players join along")
async def initive(interaction:discord.Interaction):
    view=intRollView(timeout=None)
    await interaction.response.send_message(view=view,embed=view.embed.embed())
    message = await interaction.original_response()
    db['int_ids'][message.id] = {'values':[],'players':[],'npcs':[]}
    cache.add(message.id)


Rollgroup.add_command(dmg)
Rollgroup.add_command(roll)
Rollgroup.add_command(psyc)
Rollgroup.add_command(initive)
bot.add_command(Rollgroup)

#-------------------------------------------------------------
# Weapon commands classes
#-------------------------------------------------------------

async def weapon_autocomplete(interaction: discord.Interaction,current: str,) -> list[app_commands.Choice[str]]:
    weapons = db['user_db'][interaction.user.id]['weapons']
    return [app_commands.Choice(name=weapons[weapon]['name'], value=weapons[weapon]['name']) for weapon in weapons if current.lower() in weapon.lower()][:25]

class WepPage1(ui.Modal, title = "Character Sheet | Overview"):
    def __init__(self,user):
        super().__init__()
        self.user = user
    answer1= ui.TextInput(label="● Name:", style=discord.TextStyle.short, placeholder="What is the weapon's Name")
    answer2= ui.TextInput(label="● About:", style=discord.TextStyle.long, max_length=1000, placeholder='Once upon a time in the lands of Sector Thettra...')
    answer3= ui.TextInput(label="● Modifiers:", style=discord.TextStyle.short, placeholder="Roll modifiers of the weapon (in numbers)")
    answer4= ui.TextInput(label="● Penetration:", style=discord.TextStyle.short, placeholder="Penetration of the weapon")
    answer5= ui.TextInput(label="● Dmg Type:", style=discord.TextStyle.short, placeholder="Damage type of the weapon")


    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Weapon Sheet | Overview", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer1.label, value=f'{self.answer1}', inline=False)
        embed.add_field(name='● Used by:', value=f'<@{self.user.id}>', inline=False)
        embed.add_field(name=self.answer3.label, value=f'{self.answer3}', inline=False)
        embed.add_field(name=self.answer4.label, value=f'{self.answer4}', inline=False)
        embed.add_field(name=self.answer5.label, value=f'{self.answer5}', inline=False)
        embed.add_field(name=self.answer2.label, value=f'{self.answer2}', inline=False)
        embed.set_footer(text='Weapon Sheet | page 1')
        wep = {}
        wep['owner'] = self.user.id
        wep['name'] = str(self.answer1)
        wep['bio'] = str(self.answer2)        
        wep['pent'] = str(self.answer4)
        wep['type'] = str(self.answer5)
        try:
            wep['mods'] = int(str(self.answer3))
        except:
            await interaction.response.send_message('You can only assign numerical values as modifiers!')
            return
        if not interaction.user.id in db['user_db']:
            db['user_db'][interaction.user.id] = {}
        if 'weapons' in db['user_db'][interaction.user.id]:
            db['user_db'][interaction.user.id]['weapons'][wep['name']] = wep
        else:
            db['user_db'][interaction.user.id]['weapons'] = {wep['name']:wep}
            print(db['user_db'][interaction.user.id])
        await interaction.response.send_message(embed=embed)

#-------------------------------------------------------------
# Weapon commands functions
#-------------------------------------------------------------

Wepgroup = app_commands.Group(name="weapon", description="Everything related to your weapons")

@app_commands.command(name='create')
async def wepCreate(inter:discord.Interaction):
    await inter.response.send_modal(WepPage1(inter.user))

@app_commands.command(name='delete')
@app_commands.autocomplete(weapon=weapon_autocomplete)
async def wepDelete(inter:discord.Interaction,weapon:str):
    if not 'weapons' in db['user_db'][inter.user.id]:
        await inter.response.send_message('you have no weapons to delete!')
        return
    if weapon in db['user_db'][inter.user.id]['weapons']:
        db['user_db'][inter.user.id]['weapons'].pop(weapon)
        await inter.response.send_message(f'{weapon} has been deleted from your arsenal')
    else:
        await inter.response.send_message('Weapon not found')

@app_commands.command(name='list')
async def wepList(inter:discord.Interaction):
    if 'weapons' in db['user_db'][inter.user.id]:
        if db['user_db'][inter.user.id]['weapons']:
            header=['Name','Modifier','Description']
            rows =  [[db['user_db'][inter.user.id]['weapons'][x]['name'],db['user_db'][inter.user.id]['weapons'][x]['mods'],db['user_db'][inter.user.id]['weapons'][x]['bio'][:25]] for x in db['user_db'][inter.user.id]['weapons']]
            m=tabulate.tabulate(rows, header)
            await inter.response.send_message(f"```{m[:1994]}```")
            return
    await inter.response.send_message('No weapons to list!')

@app_commands.command(name='roll')
@app_commands.autocomplete(weapon=weapon_autocomplete)
async def wepRoll(inter:discord.Interaction,weapon:str,rolls:int,multi_shot:bool=False):
    if not 'weapons' in db['user_db'][inter.user.id]:
        await inter.response.send_message('you have no weapons to roll with!')
        return
    if weapon in db['user_db'][inter.user.id]['weapons']:
        wep = db['user_db'][inter.user.id]['weapons'][weapon]
        mods = wep['mods']
        sides = 10
        dmgs = {1:"<:1_:1024361155818434590>",2:"<:2_:1024361158188212224>",3:"<:3_:1024361160356663379>",4:"<:4_:1024361162747428924>",5:"<:5_:1024361165272404008>",6:"<:6_:1024361169819025418>",7:"<:7_:1024361172255907910>",8:"<:8_:1024361176659931187>",9:"<:9_:1024361178778050661>",10:"<:10:1024361544642994237>"}
        total_dmg = 0
        desc=''
        if multi_shot==True:
            for i in range(int(rolls)):
                dmg = random.randint(1,sides)
                total_dmg+= dmg+mods
                desc = desc+dmgs[dmg]
        else:
            for i in range(int(rolls)):
                dmg = random.randint(1,sides)
                total_dmg+= dmg
                desc = desc+dmgs[dmg]
            total_dmg+=mods
        
        emb = discord.Embed(title=f"Rolling | Weapon: {wep['name']}", color=discord.Color.from_str('#ffdd70'),description=f"**Rolls:**\n{desc}")
        emb.add_field(name='Total Damage:', value=total_dmg, inline=False)
        emb.add_field(name='Type:' ,value=wep['type'])
        emb.add_field(name='Penetration:' ,value=wep['pent'])
        await inter.response.send_message(embed=emb)
    else:
        await inter.response.send_message('Weapon not found')

Wepgroup.add_command(wepCreate)
Wepgroup.add_command(wepDelete)
Wepgroup.add_command(wepList)
Wepgroup.add_command(wepRoll)
bot.add_command(Wepgroup)

#-------------------------------------------------------------
# Datacard commands classes
#-------------------------------------------------------------

class dataPage1(ui.Modal, title = "Data Card Sheet"):
    def __init__(self,user):
        super().__init__()
        self.user = user
    answer1= ui.TextInput(label="● Name:", style=discord.TextStyle.short, placeholder="Title of the data card")
    answer2= ui.TextInput(label="● Type:", style=discord.TextStyle.short, placeholder='Type of the data, Weapon, Talent, Condition, etc;')
    answer3= ui.TextInput(label="● Description:", style=discord.TextStyle.long,max_length=1024, placeholder='The data')
    answer4= ui.TextInput(label="● Source:", style=discord.TextStyle.short, placeholder='Where the Datacard information is cited from.')

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Data Card Sheet", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer1.label, value=f'{self.answer1}', inline=False)
        embed.add_field(name='● Created by:', value=f'<@{self.user.id}>', inline=False)
        embed.add_field(name=self.answer2.label, value=f'{self.answer2}', inline=False)
        embed.add_field(name=self.answer4.label, value=f'{self.answer4}', inline=False)
        embed.add_field(name=self.answer3.label, value=str(self.answer3), inline=False)
        data = {}
        data['name'] = str(self.answer1)
        data['type'] = str(self.answer2)
        data['desc'] = str(self.answer3)
        data['source'] = str(self.answer4)
        data['user'] = interaction.user.id
        if 'datacards' not in db['server_db'][interaction.guild.id]:
            db['server_db'][interaction.guild.id]['datacards'] = [data]
        else:
            db['server_db'][interaction.guild.id]['datacards'].append(data)

        await interaction.response.send_message(embed=embed)

class dataEditPage1(ui.Modal, title = "Data Card Sheet | Editing"):
    def __init__(self,data):
        super().__init__()
        self.data = data
        self.answer1= ui.TextInput(label="● Name:", style=discord.TextStyle.short, default=self.data['name'],placeholder="Title of the data card")
        self.answer2= ui.TextInput(label="● Type:", style=discord.TextStyle.short, default=self.data['type'],placeholder='Type of the data, Weapon, Talent, Condition, etc;')
        self.answer3= ui.TextInput(label="● Description:", style=discord.TextStyle.long,max_length=1024, default=self.data['desc'],placeholder='The data')
        self.answer4= ui.TextInput(label="● Source:", style=discord.TextStyle.short, default=self.data['source'],placeholder='Where the Datacard information is cited from.')
        self.add_item(self.answer1)
        self.add_item(self.answer2)
        self.add_item(self.answer3)
        self.add_item(self.answer4)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "Data Card Sheet", color=discord.Color.from_str('#ffdd70'))
        embed.add_field(name=self.answer1.label, value=f'{self.answer1}', inline=False)
        embed.add_field(name='● Created by:', value=f'<@{self.data["user"]}>', inline=False)
        embed.add_field(name=self.answer2.label, value=f'{self.answer2}', inline=False)
        embed.add_field(name=self.answer4.label, value=f'{self.answer4}', inline=False)
        embed.add_field(name=self.answer3.label, value=str(self.answer3), inline=False)
        self.data['name'] = str(self.answer1)
        self.data['type'] = str(self.answer2)
        self.data['desc'] = str(self.answer3)
        self.data['source'] = str(self.answer4)
        await interaction.response.send_message(embed=embed)

#-------------------------------------------------------------
# Datacard commands functions
#-------------------------------------------------------------

def search(name,_type,_keywords,interaction):
    if _keywords:
        keywords = _keywords.split(',')
    q = []
    for item in db['server_db'][interaction.guild.id]['datacards']:
        ratio = 0
        if name:
            ratio += round(SequenceMatcher(None, name, item['name']).ratio(),3)
        if _type:
            ratio += round(SequenceMatcher(None, _type, item['type']).ratio(),3)
        
        if _keywords:
            for keyword in keywords:
                if keyword in item['desc']:
                    ratio+=1/len(keywords)
        if ratio>0.6:
            q.append((item,ratio))
    q = sorted(q, key=lambda t:t[1])
    q.reverse()

    return q


Datagroup = app_commands.Group(name="datacard", description="Commands related to making reference data cards")

@app_commands.command(name='create',description="Create a data card for reference!")
async def dataCreate(interaction:discord.Interaction):
    if aclient.canDo(interaction.user,'Create'):
        await interaction.response.send_modal(dataPage1(interaction.user))
    else:
        await interaction.response.send_message("You aren't allowed to create character sheets/data cards, contact an admin if you think this is an error")

@app_commands.command(name='search',description="grad list of datacards for reference!")
@app_commands.describe(keywords='Make sure to separate the words/sentences using a comma')
async def dataSearch(interaction:discord.Interaction,name:str=None,type:str=None,keywords:str=None,id:int=None):
    if name==None and type==None and keywords==None and id==None:
        await interaction.response.send_message("Provide at least one parameter to search")
        return
    _type = str(type)
    type = aclient.type
    if 'datacards' in db['server_db'][interaction.guild.id]:
        if id==None:
            print(type(keywords))
            q = search(name,_type,keywords,interaction)
            header=['Name','Type','Description','ID']
            rows =  [[item['name'],item['type'],item['desc'],db['server_db'][interaction.guild.id]['datacards'].index(item)] for item,r in q]
            m=tabulate.tabulate(rows, header)
            await interaction.response.send_message(f"```{m[:1994]}```")
        else:
            print(id)
            if id <= len(db['server_db'][interaction.guild.id]['datacards']):
                emb = discord.Embed(title='Datacard Sheet',color=discord.Color.from_str('#ffdd70'))
                emb.add_field(name='● Name:', value=db['server_db'][interaction.guild.id]['datacards'][id]['name'], inline=False)
                emb.add_field(name='● Created by:', value=f"<@{db['server_db'][interaction.guild.id]['datacards'][id]['user']}>", inline=False)
                emb.add_field(name='● Type:', value=db['server_db'][interaction.guild.id]['datacards'][id]['type'], inline=False)
                emb.add_field(name='● Source:', value=db['server_db'][interaction.guild.id]['datacards'][id]['source'], inline=False)
                emb.add_field(name='● Description:', value=db['server_db'][interaction.guild.id]['datacards'][id]['desc'], inline=False)
                await interaction.response.send_message(embed=emb)
            else:
                await dataSearch.callback(interaction,name,type,None)
    else:
        await interaction.response.send_message('This server has no data cards')

@is_gm()
@app_commands.command(name='list',description="view all the datacard names and other info")
async def dataList(interaction:discord.Interaction):
    if 'datacards' in db['server_db'][interaction.guild.id]:
        header=['Name','Type','Description','ID']
        rows =  [[db['server_db'][interaction.guild.id]['datacards'][x]['name'],db['server_db'][interaction.guild.id]['datacards'][x]['type'],db['server_db'][interaction.guild.id]['datacards'][x]['desc'][:25],x] for x in range(len(db['server_db'][interaction.guild.id]['datacards']))]
        m=tabulate.tabulate(rows, header)
        await interaction.response.send_message(f"```{m[:1994]}```")

@app_commands.command(name='view',description="view a datacard and other info")
async def dataView(interaction:discord.Interaction,id:int):
    if id>len(db['server_db'][interaction.guild.id]['datacards']):
        await interaction.response.send_message('Invalid ID',ephemeral=True)
    else:
        emb = discord.Embed(title='Datacard Sheet',color=discord.Color.from_str('#ffdd70'))
        emb.add_field(name='● Name:', value=db['server_db'][interaction.guild.id]['datacards'][id]['name'], inline=False)
        emb.add_field(name='● Created by:', value=f"<@{db['server_db'][interaction.guild.id]['datacards'][id]['user']}>", inline=False)
        emb.add_field(name='● Type:', value=db['server_db'][interaction.guild.id]['datacards'][id]['type'], inline=False)
        emb.add_field(name='● Source:', value=db['server_db'][interaction.guild.id]['datacards'][id]['source'], inline=False)
        emb.add_field(name='● Description:', value=db['server_db'][interaction.guild.id]['datacards'][id]['desc'], inline=False)
        await interaction.response.send_message(embed=emb)

@app_commands.command(name='edit', description="Edit the datacards")
async def dataEdit(interaction:discord.Interaction,id:int):
    if id>len(db['server_db'][interaction.guild.id]['datacards']):
        await interaction.response.send_message('Invalid ID',ephemeral=True)
        return
    roles = [role.id for role in interaction.user.roles]
    if interaction.user.guild_permissions.administrator:
        pass
    elif db['server_db'][interaction.guild.id]['admin'] in roles:
        pass
    elif db['server_db'][interaction.guild.id]['gm'] in roles:
        pass
    elif interaction.user.id == db['server_db'][interaction.guild.id]['datacards'][id]['user']:
        pass
    else:
        await interaction.response.send_message("Edit Denied: You don't own this datacard nor are you an admin",ephemeral=True)
        return
    await interaction.response.send_modal(dataEditPage1(data=db['server_db'][interaction.guild.id]['datacards'][id]))

@app_commands.command(name='delete',description='Delete a datacard')
async def dataDelete(interaction:discord.Interaction,id:int):
    if id>len(db['server_db'][interaction.guild.id]['datacards']):
        await interaction.response.send_message('Invalid ID',ephemeral=True)
        return
    roles = [role.id for role in interaction.user.roles]
    if interaction.user.guild_permissions.administrator:
        pass
    elif db['server_db'][interaction.guild.id]['admin'] in roles:
        pass
    elif db['server_db'][interaction.guild.id]['gm'] in roles:
        pass
    elif interaction.user.id == db['server_db'][interaction.guild.id]['datacards'][id]['user']:
        pass
    else:
        await interaction.response.send_message("Delete Denied: You don't own this datacard nor are you an admin",ephemeral=True)
        return
    db['server_db'][interaction.guild.id]['datacards'].pop(id)
    await interaction.response.send_message("Data Card Removed.")

Datagroup.add_command(dataCreate)
Datagroup.add_command(dataSearch)
Datagroup.add_command(dataEdit)
Datagroup.add_command(dataDelete)
Datagroup.add_command(dataList)
Datagroup.add_command(dataView)
bot.add_command(Datagroup)

@bot.error
async def on_error(*args,**kwargs):
    for arg in args:
        if isinstance(arg, discord.app_commands.errors.CommandInvokeError):
            if isinstance(arg.__cause__,KeyError):
                await args[0].response.send_message(f'> UnknownError: if the issue persists contact the developer with server id and the screenshot of the following error\n {args}')
                await aclient.on_guild_join(args[0].guild)
            else:
                raise arg

#-------------------------------------------------------------
# Help command classes
#-------------------------------------------------------------


#-------------------------------------------------------------
# Help command functions
#-------------------------------------------------------------

@bot.command(name='help',description="stop it, get some help")
async def help(inter:discord.Interaction, command:str=None):
    if not command:
        embed = discord.Embed(title="Help section", color=discord.Color.from_str('#ffdd70'))
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1030493512283717753/1030493572094513242/bot.png")
        embed.add_field(name='Character 👕',value='`create`, `edit`, `image`, `view`, `set`, `delete`')
        embed.add_field(name='Weapons ⚔️',value='`create`, `delete`, `list`, `roll`')
        embed.add_field(name='Admin 🛠️',value='`create`, `edit`, `delete`')
        embed.add_field(name='Gm 🧙‍♂️',value='`create`, `edit`, `exp`')
        embed.add_field(name='Rolls 🎲',value='`dmg`, `char`, `psyc`, `initiative`')
        embed.add_field(name='Datacard 📜',value='`create`, `search`, `edit`, `delete`, `list`, `view`')
        embed.add_field(name='Config ⚙️',value='`admin`, `gm`, `allow`')
        await inter.response.send_message(embed=embed)
        return
    {'roll': ['dmg', 'char', 'psyc', 'initiative'], 'char': ['create', 'edit', 'image', 'view', 'visibility', 'set', 'delete'], 'admin': ['create', 'edit', 'delete'], 'config': ['admin', 'gm', 'allow'], 'gm': ['create', 'edit', 'exp'], 'datacard': ['create', 'search', 'edit', 'delete', 'list'], 'weapon': ['create', 'delete', 'list', 'roll'], 'help': ['command']}
    c = await bot.fetch_commands()
    l = {}
    for i in c:
        if i.options:
            l[i.name]=[j.name for j in i.options]
    print(l)

token=config['token']

if config['isFirebase']:
    firebase = pyrebase.initialize_app(config["firebaseConfig"])
    storage = firebase.storage()
    try:
        with open('root.json','rb') as f:
            db = pickle.load(f)
        storage.child('root.json').download(config['firebaseConfig']['storageBucket'],'root.json')
        storage.child('backup.json').download(config['firebaseConfig']['storageBucket'],'backup.json')
    except Exception as e:
        if isinstance(e,EOFError):
            with open('root.json', 'wb') as f:
                db = {'user_db':{},'server_db':{},'int_ids':{}}
                pickle.dump(db,f)
            print("Warning: Empty DB file found! data has been reset.")
        elif isinstance(e,FileNotFoundError):
            with open('root.json', 'wb') as f:
                db = {'user_db':{},'server_db':{},'int_ids':{}}
                pickle.dump(db,f)
            print("Warning: DB file not found new created!")
        else:
            raise e
else:
    try:
        conn = sqlite3.connect("root.db")
        c = conn.cursor()
        c.execute("SELECT * FROM data WHERE id = 1")
        data = c.fetchone()[0]
        if not data:
            raise EOFError("EMPTY SQL DB")
        # with open('root.json','rb') as f:
        #     db = pickle.load(f)
        db = json.loads(data)
    except Exception as e:
        if isinstance(e,EOFError):
            conn = sqlite3.connect("root.db")
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS data (id int, dd text)")
            db = {'user_db':{},'server_db':{},'int_ids':{}}
            dbs = json.dumps(db)
            c.execute("INSERT INTO data (id,dd) VALUES (?,?)",(1,dbs))
            conn.commit()
            # with open('root.json', 'wb') as f:
            #     db = {'user_db':{},'server_db':{},'int_ids':{}}
            #     pickle.dump(db,f)
            print("Warning: Empty DB file found! data has been reset.")
        # elif isinstance(e,FileNotFoundError):
        #     with open('root.json', 'wb') as f:
        #         db = {'user_db':{},'server_db':{},'int_ids':{}}
        #         pickle.dump(db,f)
        #     print("Warning: DB file not found new created!")
        else:
            raise e
aclient.run(token)