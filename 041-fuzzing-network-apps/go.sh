#!/bin/bash
/home/gynvael/en_eps_041/afl-2.52b/afl-g++ serv_harness.cpp -Wno-format-security -Wno-unused-result
g++ -ggdb serv_harness.cpp -Wno-format-security -Wno-unused-result -o a.dbg

cp ./a.out /home/gynvael/en_eps_041/afl-2.52b/
cp ./a.dbg /home/gynvael/en_eps_041/afl-2.52b/
cd /home/gynvael/en_eps_041/afl-2.52b/

./afl-fuzz \
  -i ./in \
  -o ./out \
  -f file \
  -- ./a.out @@



