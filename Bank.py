import discord
from discord.ext import commands
import json
import os
import random

client = commands.Bot(command_prefix = "-")
client.remove_command('help')

mainshop = [{"name":"Watch","price":1000,"description":"Time"},
	    {"name":"Example Item","price":69,"description":"Example"}]


@client.event
async def on_ready():
    print("Bank opened")
	
@client.command()
async def bal(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title = f"{ctx.author.name}'s balance",color = discord.Color.blurple())
    em.add_field(name = "Wallet balance",value = wallet_amt)
    em.add_field(name = "Bank balance",value = bank_amt)
    await ctx.send(embed = em)


@client.command()
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author


    earnings = random.randrange(101)

    await ctx.send(f"Someone gabe u {earnings} monee!!")


     
    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json","w") as f:
        json.dump(users,f)


@client.command()
@commands.has_permissions(administrator = True)
async def give(ctx,monee = None):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    monee = int(monee)

    await ctx.send(f"You got {monee} monee!!")


     
    users[str(user.id)]["wallet"] += monee

    with open("mainbank.json","w") as f:
        json.dump(users,f)


@client.command()
async def withdraw(ctx,amount = None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount you want to withdraw")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount>bal[1]:
        await ctx.send("You don't have that much money")
        return
    if amount<0:
        await ctx.send("Amount must be higher")
        return

    await update_bank(ctx.author,amount)
    await update_bank(ctx.author,-1*amount,"bank")

    await ctx.send(f"Withdrew {amount} monee")


@client.command()
async def dep(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("No amount is not good")
        return

    bal = await update_bank(ctx.author)
    
    amount = int(amount)
    if amount>bal[0]:
        await ctx.send("You dont hab that much monee")
        return
    if amount<0:
        await ctx.send("Amount must be higher")
        return

    await update_bank(ctx.author,-1*amount)
    await update_bank(ctx.author,amount,"bank")

    await ctx.send(f"You put {amount} in bank")



@client.command()
async def gib(ctx,member:discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)

    if amount == None:
        await ctx.send("Please enter the amount you want to withdraw")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount>bal[1]:
        await ctx.send("You don't have that much money")
        return
    if amount<0:
        await ctx.send("Amount must be higher")
        return

    await update_bank(ctx.author,-1*amount,"bank")
    await update_bank(member,amount,"bank")

    await ctx.send(f"you gabe {member} {amount} monee")



@client.command()
async def rob(ctx,member:discord.Member):
    await open_account(ctx.author)
    await open_account(member)

    bal = await update_bank(member)

    if bal[0]<100:
        await ctx.send("not worth it")
        return

    earnings = random.randrange(0, bal[0])
    

    await update_bank(ctx.author,earnings)
    await update_bank(member,-1*earnings)

    await ctx.send(f"you stole {member} {earnings} monee")

@client.command()
async def slots(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("No amount is not good")
        return

    bal = await update_bank(ctx.author)
    
    amount = int(amount)
    if amount>bal[0]:
        await ctx.send("You dont hab that much monee")
        return
    if amount<0:
        await ctx.send("Amount must be higher")
        return
    final = []
    for i in range(3):
        a = random.choice(["✡","👨🏿","🧔🏿","🎅🏿"])

        final.append(a)

    await ctx.send(str(final))
    if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
        await update_bank(ctx.author,1*amount)
        await ctx.send("You won!")
    else:
        await update_bank(ctx.author,-1*amount)
        await ctx.send("Haha you lost!")


@client.command()
async def shop(ctx):
    em = discord.Embed(title = "Shop")

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name = name, value = f"${price}|{desc}")

    await ctx.send(embed = em)


@client.command()
async def buy(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isnt there")
            return
        if res[1]==2:
            await ctx.send(f"You need more money in your wallet")
            return



    await ctx.send(f"Poggers you just baught {amount} {item}")


@client.command()
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []


    em = discord.Embed(title = "Bag")
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name = name, value = amount)    

    await ctx.send(embed = em)    


@client.command()
async def sell(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there!")
            return
        if res[1]==2:
            await ctx.send(f"You don't have {amount} {item} in your bag.")
            return
        if res[1]==3:
            await ctx.send(f"You don't have {item} in your bag.")
            return

    await ctx.send(f"You just sold {amount} {item}.")

async def sell_this(user,item_name,amount,price = None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price==None:
                price = 1* item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False,2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            return [False,3]
    except:
        return [False,3]    

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost,"wallet")

    return [True,"Worked"]


	
async def open_account(user):

    users = await get_bank_data()


    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("mainbank.json","w") as f:
            json.dump(users,f)
    return True

async def get_bank_data():
    with open("mainbank.json","r") as f:
       users = json.load(f)

    return users


async def buy_this(user,item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        return [False,2]


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            obj = {"item":item_name , "amount" : amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name , "amount" : amount}
        users[str(user.id)]["bag"] = [obj]        

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost*-1,"wallet")

    return [True,"Worked"]



async def update_bank(user,change = 0,mode = "wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("mainbank.json","w") as f:
        json.dump(users,f)
    
    bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
    return bal


@client.command(aliases = ["lb"])
async def leaderboard(ctx,x = 5):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)    

    em = discord.Embed(title = f"Top {x} Richest People" , description = "This is decided on the basis of raw money in the bank and wallet",color = discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em)


@client.command()
@commands.has_permissions(administrator = True)
async def game(ctx, *, message): # b'\xfc'
    await ctx.message.delete()
    game = discord.Game(
        name=message
    )
    await client.change_presence(activity=game)


@client.command()
async def help(ctx):
    emb = discord.Embed(
        title = 'Help',
        description = 'These are all the commands',
        colour = discord.Colour.blurple()
    )
    emb.add_field(name='bag', value='Shows the stuff you bought', inline=True)
    emb.add_field(name='bal', value='Shows how much money you have', inline=True)
    emb.add_field(name='beg', value='got no money? use this command', inline=True)
    emb.add_field(name='buy <item> <amount>', value='you want some cool stuff?', inline=True)
    emb.add_field(name='dep <amount>', value='dont want to get robbed? deposit all of your money', inline=True)
    emb.add_field(name='gib <user>', value='give someone a donation', inline=True)
    emb.add_field(name='leaderboard <Number>', value='See the richest people on the server.the higher the number the more people will be shown', inline=True)
    emb.add_field(name='rob <user>', value='steal from someones wallet', inline=True)
    emb.add_field(name='sell <item> <amount>', value='Sell your stuff', inline=True)
    emb.add_field(name='shop', value='shows a list of items', inline=True)
    emb.add_field(name='slots <amount>', value='Dont get addicted', inline=True)
    emb.add_field(name='withdraw <amount>', value='put some money from your bank in your wallet', inline=True)


    await ctx.send(embed=emb)







        


    

       


	
	
client.run("Token")
