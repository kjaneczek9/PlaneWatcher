
This program is so specific to me and the antenna plugged into a raspberry pi on my desk.

Docker bundle that runs ./dump1090 to get data off an ADS receiver, writes that data to
a file which is then read by a flask app, the flask app processes, makes it pretty, and then
updates a socket that the client html is listening to. Nothing special.

Oh yeah and the client html is plotting coordinates over apple maps, so if you theoretically tried to use this anywhere other than LAX, you wont really see anything.
:5000/ will show you the 1090 output with grounded planes excluded.

Most of Dump1090 is from an open source lib (thanks reddit), but I tweaked it a bit to work for
my use case. Mainly how it was writing data.

Note the daq container actually does nothing right now and to use the program you'll have to start
all containers, go into the daq one, and run ./entrypoint.sh. This is because I was having mad usb
port conflicts and I haven't gotten around to fixing it.

Anywho, runs with a `make run` !