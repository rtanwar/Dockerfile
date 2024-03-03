from tasks import add
#res = add.delay(2, 2)
res=add.apply_async((2,3))
#output=res.get(timeout=5)
#print(output)
print(res.state)
#add(2, 2)