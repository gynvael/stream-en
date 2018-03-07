all:
	g++ -Wall -Wextra library.cpp -o library

test: all
	#nc.traditional -e ./library -v -l -p 31337
	#socat tcp-l:31337,reuseaddr exec:"ltrace -e malloc -e free ./library"
	socat tcp-l:31337,reuseaddr exec:./library


