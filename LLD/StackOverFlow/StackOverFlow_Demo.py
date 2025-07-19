from Stack_Over_Flow import StackOvertFlow


class StackOvertFlowDemo:
    @staticmethod
    def run():
        system = StackOvertFlow()

        alice = system.create_user("Alice", "alice@example.com")
        bob = system.create_user("Bob", "bob@example.com")
        charlie = system.create_user("Charlie", "charlie@example.com")


        # Alice asks a question
        py_question = system.ask_question(alice, "How to use Python?", "I'm new to Python and I'm having trouble understanding how to use it.", ["python", "programming"])

        # Bob answers the question
        answer1 = system.answer_question(bob, py_question, "You can start by reading the official Python documentation and trying out some basic examples.")

        # Charlie comments on the question
        system.add_comment(charlie, py_question, "This is a great question, I had the same issue when I started!")
        system.add_comment(alice, answer1, "Thanks for the answer, it was really helpful! Can you give code examples?")

        # charlie votes on the question
        system.vote_question(charlie, py_question, 1)
        system.vote_answer(charlie, answer1, 1)

        # Alice accepts the answer
        system.accpet_answer(answer1)

        # Charlie asked another question
        sorting_question = system.ask_question(charlie, "How to sort dictionary in python?", "can anyone explain me how to sort dictionary based on value in decending order?", ["python", "sorting"])

        # alice answers the question
        answer2 = system.answer_question(alice, sorting_question, "You can use the sorted function with a lambda function to sort by value.")
        system.vote_answer(alice, answer2, 1)
        system.add_comment(bob, sorting_question, "Sorting dictionaries can be tricky, but it's a useful skill to have!")
        
        system.vote_question(charlie, answer2, 1)

        # print out the current state of the system
        print("Users:")
        for user in system.users.values():
            print("="* 20)
            print(vars(user))
            
        
        print("\nQuestions:")
        for question in system.questions.values():
            print("+-+"* 20)
            print(vars(question))
        
        print("\nAnswers:")
        for answer in system.answers.values():
            print("_*_*_"* 20)
            print(vars(answer))
    
        

    
if __name__ == '__main__':
    StackOvertFlowDemo.run()