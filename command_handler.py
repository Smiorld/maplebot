import copy
from discord import Member
from data_manager import LogEntry, DataManager
from datetime import datetime, timedelta

class BotCommandHandler:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    async def join(self, ctx, ign):
        """
        Handle the join command.

        Args:
            ctx (commands.Context): The context of the command.
            ign (str): In-Game Name provided with the command.
        """
        current_party_members = copy.deepcopy(self.data_manager.get_current_party_members())
        if ign not in current_party_members and len(current_party_members) < 4:
            # player can join
            # add player to party, which should create a new log row to data
            if len(current_party_members) == 0:
                is_party_paused = 0 # 如果没有buyer，默认不暂停。
            else:
                #否则取上一个log，复制它的状态
                is_party_paused = self.data_manager.logs[-1].is_party_paused
            current_party_members.append(ign)
            self.data_manager.add_log_entry(LogEntry(ign, 'join', current_party_members, is_party_paused))
            # Send a confirmation message
            await ctx.send(f"Player {ign} has joined party.")
        else:
            # If the ign is already joined, send a message indicating it
            await ctx.send(f"Player {ign} is already joined.")

    

    async def leave(self, ctx, ign):
        """
        Handle the leave command.

        Args:
            ctx (commands.Context): The context of the command.
            ign (str): In-Game Name provided with the command.
        """
        current_party_members = copy.deepcopy(self.data_manager.get_current_party_members())
        
        if ign in current_party_members:
            # player can leave
            current_party_members.remove(ign)
            
            response = self.get_the_bill(ign)

            # 如果离开的是目前最早进队的玩家，从头顺序清除partylog直到读到 仍在当前队伍的角色的join 为止
            ready2delete = []
            log_entries = self.data_manager.logs
            if log_entries[0].ign == ign:
                for log_entry in log_entries:
                    if log_entry.event_type=='join' and log_entry.ign in current_party_members:
                        break
                    ready2delete.append(log_entry)
            self.data_manager.remove_log_entries(log_entries)

            # Check if the party is empty after removing the player. 如果离开以后无玩家，清空logs
            if len(current_party_members) == 0:
                self.data_manager.remove_log_entries(self.data_manager.logs)
                self.data_manager.last_operation=None
            else :
                is_party_paused = self.data_manager.logs[-1].is_party_paused   
                self.data_manager.add_log_entry(LogEntry(ign, 'leave', current_party_members, is_party_paused))
            # Send a confirmation message
            await ctx.send(response)
        else:
            # If the ign is not in the party, send a message indicating it
            await ctx.send(f"Player {ign} is not in the party.")

    async def pause(self, ctx):
        """
        Handle the pause command.

        Args:
            ctx (commands.Context): The context of the command.
        """
        current_party_members = copy.deepcopy(self.data_manager.get_current_party_members())
        is_party_paused = 1  # Set party state to paused

        # Check if the party is already paused
        if self.data_manager.logs and self.data_manager.logs[-1].is_party_paused:
            await ctx.send("Party is already paused.")
        else:
            # Update party state to paused and create a log entry
            self.data_manager.add_log_entry(LogEntry('party', 'pause', current_party_members, is_party_paused))
            await ctx.send("Party has been paused.")

    async def resume(self, ctx):
        """
        Handle the resume command.

        Args:
            ctx (commands.Context): The context of the command.
        """
        current_party_members = copy.deepcopy(self.data_manager.get_current_party_members())
        is_party_paused = 0  # Set party state to resumed

        # Check if the party is already resumed
        if self.data_manager.logs and not self.data_manager.logs[-1].is_party_paused:
            await ctx.send("Party is already running.")
        else:
            # Update party state to resumed and create a log entry
            self.data_manager.add_log_entry(LogEntry('party', 'resume', current_party_members, is_party_paused))
            await ctx.send("Party has been resumed.")

    async def undo(self, ctx):
        """
        Handle the undo command.

        Args:
            ctx (commands.Context): The context of the command.
        """
        # Check if there are any log entries to undo
        if self.data_manager.last_operation is None:
            await ctx.send("No actions to undo.")
        else:
            # Undo the last action 
            if self.data_manager.last_operation[0] == 'remove':
                self.data_manager.add_log_entries(self.data_manager.last_operation[1])
            else:
                self.data_manager.remove_log_entries(self.data_manager.last_operation[1])
            self.data_manager.last_operation = None
            await ctx.send("Undo the last operation successfully.")


    async def help(self, ctx):
        """
        Handle the help command.

        Args:
            ctx (commands.Context): The context of the command.
        """
        # TODO output commands list
        pass

    async def party(self, ctx):
        """
        Handle the party command.

        Args:
            ctx (commands.Context): The context of the command.
        """
        current_party_members = self.data_manager.get_current_party_members()
        await ctx.send(f'party members: {current_party_members}')

    async def save(self, ctx):
        """
        Handle the save command.

        Args:
            ctx (commands.Context): The context of the command.
        """
        # Implementation for save command
        self.data_manager.save_logs()
        await ctx.sned('logs saved to files successful')


    def get_the_bill(self, ign):
        response = ''
        currenttime = datetime.utcnow()
        # 输出从该玩家入队到离队的所有log，并统计各队伍人数下该玩家待了多久
        inparty_flag = 0
        leechtime = { 1: timedelta(), 2: timedelta(), 3: timedelta(), 4: timedelta()}
        last_partynumber = 0
        log_entries = self.data_manager.logs
        last_log = log_entries[0]
        is_pause = 0
        for log_entry in log_entries:
            if inparty_flag == 0:
                if log_entry.ign == ign and log_entry.event_type == 'join':
                    # 该玩家进队的log
                    inparty_flag = 1
                    response += f"{ ign } joined at { (log_entry.to_dict())['timestamp'] }, party members: { ' '.join(log_entry.party_members) }\n"
                    is_pause = log_entry.is_party_paused
                    last_log = log_entry
                    last_partynumber = len(log_entry.party_members)
            else:
                response += f"{ log_entry.ign } { log_entry.event_type }d at { (log_entry.to_dict())['timestamp'] }, party members: { ' '.join(log_entry.party_members) }\n"
                if is_pause == 0 :
                    leechtime[last_partynumber] += log_entry.timestamp - last_log.timestamp
                is_pause = log_entry.is_party_paused
                last_log = log_entry
                last_partynumber = len(log_entry.party_members)
        response += f"{ign} left at { currenttime.strftime('%b %d, %Y %H:%M:%S GMT') }\n"
        if is_pause ==0 :
            leechtime[last_partynumber] += currenttime - last_log.timestamp
        hours = []
        hours.append(leechtime[1].seconds/3600.0)
        hours.append(leechtime[2].seconds/3600.0)
        hours.append(leechtime[3].seconds/3600.0)
        hours.append(leechtime[4].seconds/3600.0)
        # 输出其在不同队伍人数下待的时间
        response += f'player {ign} leech in solo: {hours[0]} hrs, duo: {hours[1]} hrs, 3 buyers: {hours[2]} hrs, 4 buyers: {hours[3]} hrs.'

        # TODO: 接受系数设定并直接输出应付金额

        return response