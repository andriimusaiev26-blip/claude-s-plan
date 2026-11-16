
import time


class Quiz:
    def __init__(self, questions):
        # Принимаем список вопросов или таблицу pandas
        if hasattr(questions, "to_dict"):
            questions = questions.to_dict(orient="records")

        self.questions = list(questions)
        self.current_step = 0
        self.results = []
        self.start_time = time.monotonic()

    def get_question(self):
        # Возвращаем текущий вопрос
        if self.current_step < len(self.questions):
            return self.questions[self.current_step]
        return None

    def check_answer(self, answer):
        question = self.get_question()

        if question is None:
            return None

        # Время, потраченное на ответ
        elapsed = round(time.monotonic() - self.start_time, 2)
        time_limit = float(question.get("time_limit", 20))

        # Проверяем ответ и время
        correct = (
            str(answer).strip().upper()
            == str(question["correct_answer"]).strip().upper()
        )
        late = elapsed > time_limit

        # Критическая ошибка задаётся в CSV
        critical = (
            str(question.get("critical_on_error", "false")).lower()
            in ("true", "1", "yes")
            and not correct
        )

        result = {
            "step": self.current_step + 1,
            "correct": correct and not late,
            "mistake": not correct or late,
            "critical": critical,
            "time": elapsed,
            "late": late
        }

        self.results.append(result)
        self.current_step += 1

        # Запускаем таймер следующего вопроса
        self.start_time = time.monotonic()

        return result

    def is_finished(self):
        return self.current_step >= len(self.questions)

    def get_summary(self):
        if not self.results:
            return None

        slowest = max(
            self.results,
            key=lambda result: result["time"]
        )

        return {
            "steps": len(self.results),
            "correct": sum(r["correct"] for r in self.results),
            "mistakes": sum(r["mistake"] for r in self.results),
            "critical_mistakes": sum(r["critical"] for r in self.results),
            "total_time": round(
                sum(r["time"] for r in self.results), 2
            ),
            "slowest_step": slowest["step"]
        }
