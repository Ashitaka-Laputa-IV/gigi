from gigi import gigi

my_gigi = gigi()

while True:
    message = input("user: ")
    if message == "exit":
        break
    response = my_gigi.talk(message)
    print("gigi:", response)
