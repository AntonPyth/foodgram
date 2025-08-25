import sys

print("=== sys.path ===")
for p in sys.path:
    print(p)

print("\n=== Импорт foodgram.constants ===")
try:
    import backend.foodgram.foodgram.constants as const
    print("✅ Успешно импортирован!")
    print("Содержимое:", dir(const))
except ModuleNotFoundError as e:
    print("❌ Ошибка импорта:", e)
