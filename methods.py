from datetime import datetime
import json, copy

last_partylog = None  # 用来undo上一个错误的option

def get_currentparty(partylog: dict):
    party = []
    # log从头往尾读。读到加入就进队，读到离队就离队。
    for key in partylog.keys():
        if key.endswith('join'):
            party.append(key[:-5])
        if key.endswith('leave'):
            member = key[:-6]
            if member in party:
                party.remove(member)
    return party



def join_party(partylog: dict, party: list, ign: str):
    global last_partylog
    if party_add_member(party, ign):
        # 如果这个角色可以加入当前的队伍
        # 保存当前状态，用于undo
        last_partylog = copy.deepcopy(partylog)
        # 更新partylog
        partylog[f'{ign}_join']={'party': copy.deepcopy(party), 'time':int(datetime.utcnow().timestamp())}
        # 保存改变。
        partylog_save(partylog)
        return True
    else:
        # 如果加入失败（已在队伍）
        return False


def leave_party(partylog: dict, party: list, ign: str):
    global last_partylog
    if party_remove_member(party, ign):
        # 如果这个角色可以离开当前队伍
        # 保存当前状态，用于undo
        last_partylog = copy.deepcopy(partylog)

        # 离队需要输出log和bill
        response = get_the_bill(partylog, party, ign)

        # 如果离开的是目前最早进队的玩家，从头顺序清除partylog直到读到 仍在当前队伍的角色的join 为止
        keys = list(partylog.keys())
        tmp_partylog = copy.deepcopy(partylog)
        if keys[0] == f'{ign}_join':
            for key in partylog.keys():
                if key.endswith('join') and key[:-5] in party:
                    break
                del tmp_partylog[key]
        partylog = copy.deepcopy(tmp_partylog)

        # 更新partylog
        partylog[f'{ign}_leave']={'party': copy.deepcopy(party), 'time':int(datetime.utcnow().timestamp())}
        # 保存改变。
        partylog_save(partylog)
        
        return response
    else:
        # 如果离开失败（不在队伍）
        return False

def undo_operation(partylog: dict, party: list):
    global last_partylog
    if last_partylog:
        partylog = copy.deepcopy(last_partylog)
        party = get_currentparty(partylog)
        last_partylog = None
        return True
    return False

def party_add_member(party: list, ign: str):
    if ign in party:
        return False
    party.append(ign)
    return True

def party_remove_member(party: list, ign: str):
    if ign not in party:
        return False
    party.remove(ign)
    return True

def get_the_bill(partylog: dict, party: list, ign: str):
    response = ''
    currenttimestamp = int(datetime.utcnow().timestamp())
    # 输出从该玩家入队到离队的所有log，并统计各队伍人数下该玩家待了多久
    inparty_flag = 0
    leechtime = { 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    last_timestamp = 0
    last_partynumber = 0
    for key in partylog.keys():
        if inparty_flag == 0:
            if key[:-5]==ign:
                inparty_flag = 1
                response += f'player { key } party at { timestamp2str(partylog[key]["time"]) }, party members {partylog[key]["party"]}\n'
                last_timestamp = partylog[key]["time"]
                last_partynumber = len(partylog[key]["party"])
        else:
            response += f'player { key } party at { timestamp2str(partylog[key]["time"]) }, party members {partylog[key]["party"]}\n'
            leechtime[last_partynumber] += partylog[key]["time"] - last_timestamp
    response += f'player {ign}_leave party at { timestamp2str(currenttimestamp) }, party members { party }\n'
    leechtime[last_partynumber] += currenttimestamp - last_timestamp
    leechtime[1]=round(leechtime[1]/3600.0,3)
    leechtime[2]=round(leechtime[2]/3600.0,3)
    leechtime[3]=round(leechtime[3]/3600.0,3)
    leechtime[4]=round(leechtime[4]/3600.0,3)
    # 输出其在不同队伍人数下待的时间
    response += f'{ign} leech in solo: {leechtime[1]} hrs, duo: {leechtime[2]} hrs, 3 buyers: {leechtime[3]} hrs, 4 buyers: {leechtime[4]} hrs.'

    return response
    

def partylog_save(partylog: dict):
    with open('partylog.json','w') as file:
        jsonstring = json.dumps(partylog)
        file.write(jsonstring)

def timestamp2str(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%b %d, %Y %H:%M:%S GMT')
