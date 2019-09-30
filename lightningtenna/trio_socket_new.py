import trio
from itertools import count
from utilities import chunk_to_list

CHUNK_SIZE = 210
PORT = 9733

CONNECTION_COUNTER = count()


async def sender(args):
    """sends data from the thread out via the socket
    """
    socket_stream, receive_from_thread = args
    print(f"send channel: started!")
    # get data from the mesh queue
    async for data in receive_from_thread:
        # send it out via the socket
        await socket_stream.send_all(data)


async def receiver(args):
    """receives data from the socket and sends it to the thread
    """
    socket_stream, send_to_thread = args
    print(f"recv socket: started!")
    async for data in socket_stream:
        # add received data to thread_stream queue in 210B chunks
        async for chunk in chunk_to_list(data, CHUNK_SIZE):
            await send_to_thread.send(chunk)
    print(f"recv socket: connection closed")


async def server(socket_stream, send_to_thread, receive_from_thread):
    """Accepts new connections
    """
    ident = next(CONNECTION_COUNTER)
    try:
        async with socket_stream:
            async with trio.open_nursery() as nursery:
                nursery.start_soon(sender, [socket_stream, receive_from_thread])
                nursery.start_soon(receiver, [socket_stream, send_to_thread])
    except Exception as exc:
        print(f"server {ident}: crashed: {exc}")


async def main():
    send_to_thread, receive_from_trio = trio.open_memory_channel(50)
    send_to_trio, receive_from_thread = trio.open_memory_channel(50)

    # I need to pass these channels into the server() fn?
    await trio.serve_tcp(server, PORT)


trio.run(main)