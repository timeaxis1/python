import asyncio
import socket
# Specify the server's IP address and port
server_ip = '192.168.40.247'                #10.50.171.209 
server_port = 62437

# Store the process objects in a dictionary for later reference
processes = {}

async def monitor_process(key):
    process = processes.get(key)
    if not process:
        return
    await process.wait()
    if key in processes:
        del processes[key]

async def handle_message(message):
    start_messages = ['dance1', 'shakehead2', 'bow3', 'caught4']
    stop_messages_map = {
        'dancestop1': 'dance1',
        'shakeheadstop2': 'shakehead2',
        'bowstop3': 'bow3',
        'caughtstop4': 'caught4'
    }

    if message in start_messages:
        if message not in processes:
            try:
                process = await asyncio.create_subprocess_exec('python3', f'Id{message[-1]}.py')
                processes[message] = process
                asyncio.create_task(monitor_process(message))
            except Exception as e:
                print(f"Error starting process for {message}: {e}")
    elif message in stop_messages_map:
        key = stop_messages_map[message]
        if key in processes:
            processes[key].terminate()
            del processes[key]

async def main():
    reader, writer = await asyncio.open_connection(server_ip, server_port)

    while True:
        data = await reader.read(100)
        if not data:
            break
        try:
            message = data.decode()
            await handle_message(message)
        except UnicodeDecodeError:
            print("Received invalid data from the server")

    writer.close()
    await writer.wait_closed()

asyncio.run(main())
