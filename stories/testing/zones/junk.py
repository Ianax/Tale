rooms={
    'livingroom' : {'location':
      {'name':"Living room",
       'descr': "The living room in your home in the new testing story."
       },
      'exits':'out',
      'doors':'out',
     },
    'closet' : {'location':
      {'name':"Closet",
       'descr': "A small room."
       },
      'exits':'out'
    }
}

for room in rooms.keys():
    print(rooms[room])
