```python
with open('all_unicode_char.txt', 'wb') as f:
    err_nums = 0
    true_nums = 0
    for i in range(1, pow(2, 19)):
        try:
            s = chr(i).encode('utf8')
        except UnicodeEncodeError:
            err_nums += 1
            s = None
        if s:
            f.write(s)
            true_nums += 1
    print(
        'the true add error nums equals range(1, pow(2,19)):',
        (err_nums + true_nums) == len(range(1,pow(2,19)))
    )

```

unicode中文范围
U4e00-u9fa5 


```python
import re
# import jsonpath
# jsonpath.jsonpath(
#     {"l":0,"tx":{"b":[8]},"b":[1,2,9]},
#     "$..b[?(8 not in @)]")
l=re.match('[\u4e00-\u9fa5 ]', '那就')
l=re.match(r'[\u4e00-\u9fa5 ]', '那就')
pp='xs'
```
