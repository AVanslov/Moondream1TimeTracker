import moondream as md

model = md.vl(model="./moondream-0_5b-int8.mf.gz")  # Инициализация модели

# Проверьте, является ли объект PyTorch моделью
print(type(model))
