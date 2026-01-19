inbox_msg=[]
def msg_coming(l):
    inbox_msg.append(l)
def msg_sending():
    for i in inbox_msg:
        print(i)