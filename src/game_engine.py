import random

class GameEngine:
    def __init__(self):
        self.current_step = 2
        self.current_number = 0
        self.next_number = 0
        self.options = []
        self.score = 0
        self.errors = 0
        self.max_errors = 3
        self.time_limit = 5
        self.is_active = False

    def start_game(self, step, time_limit, max_errors):
        self.current_step = step
        self.current_number = random.randint(1, 20)
        self.score = 0
        self.errors = 0
        self.is_active = True
        self.time_limit = time_limit
        self.max_errors = max_errors
            
        self.generate_question()

    def generate_question(self):
        self.next_number = self.current_number + self.current_step
        
        # Generate options
        options = [self.next_number]
        while len(options) < 3:
            wrong = self.next_number + random.choice([-2, -1, 1, 2, 3, 4, 5]) * self.current_step
            if wrong > 0 and wrong not in options:
                options.append(wrong)
        
        random.shuffle(options)
        self.options = options
        return self.current_number, self.options

    def check_answer(self, selected_number):
        if selected_number == self.next_number:
            self.score += 1
            self.current_number = self.next_number
            self.generate_question()
            return True
        else:
            self.errors += 1
            return False
