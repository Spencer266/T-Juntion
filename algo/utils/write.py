def writeListToFile(my_list, dest):
  with open(dest, 'w') as f:
    for i in my_list:
      f.write(f'{i}\n')
    f.close()