# seconds.py
# Вспомогательный виджет-таймер:
# - показывает текст "Прошло секунд: N"
# - каждую секунду увеличивает N
# - по достижении total секунд устанавливает done=True и сам останавливается

from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import BooleanProperty

class Seconds(Label):
    # Свойство done можно "биндить": когда становится True, срабатывают подписчики
    done = BooleanProperty(False)

    def __init__(self, total: int, **kwargs):
        super().__init__(**kwargs)
        self.done = False       # таймер ещё не закончен
        self.current = 0        # сколько секунд прошло
        self.total = total      # целевое число секунд
        self.text = "Прошло секунд: " + str(self.current)

    def restart(self, total: int, **kwargs):
        """
        Полный перезапуск таймера с новым количеством секунд:
        - сбрасывает текущие значения
        - запускает отсчёт
        """
        self.done = False
        self.total = total
        self.current = 0
        self.text = "Прошло секунд: " + str(self.current)
        self.start()

    def start(self):
        """Запускаем тиканье раз в секунду: Kivy будет вызывать change(dt)"""
        Clock.schedule_interval(self.change, 1)

    def change(self, dt: float):
        """
        change вызывается каждые ~1 сек:
        - увеличиваем счётчик
        - обновляем текст
        - если достигли цели, помечаем done=True и возвращаем False (это останавливает Clock)
        """
        self.current += 1
        self.text = "Прошло секунд: " + str(self.current)
        if self.current >= self.total:
            self.done = True
            return False  # сигнал Clock: остановить вызовы change
