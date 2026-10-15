# модуль

использование - 
for word in str:
    if conatins_word(word, filepath)

filepath - словарь, в котором каждое слово заканчивается \n

# Дружит только с англ словами, иначе ему оч плохо
# ФАЙЛЫ ТОЛЬКО LF, UTF-8

# сборка

```bash
python3 setup.py build_ext --inplace
```

# использовать
```python
import file_search
dct = "words.txt" 
try:
    if file_search.contains_word(dct, "linux"):
        print("Found!")
    else:
        print("Not found.")
except OSError as e:
    print(f"Error: {e}")
```