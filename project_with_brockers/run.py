from tasks import start_processing

if __name__ == "__main__":
    start_processing.apply_async()  # Запускаем задачу
    # start_processing()  # В режиме отладки
