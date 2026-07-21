# Person 클래스: 가장 기본이 되는 사람을 나타내는 틀입니다.
# 여기서는 사람의 번호(id)와 이름(name)을 저장합니다.
class Person:
    # 생성자: 객체를 만들 때 처음에 필요한 값을 받아 저장합니다.
    def __init__(self, id, name):
        self.id = id          # 사람의 번호를 저장합니다.
        self.name = name      # 사람의 이름을 저장합니다.

    # printInfo 메서드: 저장된 정보를 화면에 출력합니다.
    def printInfo(self):
        print(f"ID: {self.id}, Name: {self.name}")


# Manager 클래스: Person 클래스를 상속받아서 만든 클래스입니다.
# Person의 기능을 그대로 쓰면서, 직급(title)이라는 새 정보를 추가합니다.
class Manager(Person):
    def __init__(self, id, name, title):
        super().__init__(id, name)   # Person 클래스의 생성자를 먼저 실행합니다.
        self.title = title           # 관리자의 직급을 저장합니다.

    # 자기 정보와 직급까지 함께 출력합니다.
    def printInfo(self):
        super().printInfo()          # Person의 printInfo를 먼저 실행합니다.
        print(f"Title: {self.title}")


# Employee 클래스: Person 클래스를 상속받아서 만든 클래스입니다.
# Person의 기능을 그대로 쓰면서, 기술(skill)이라는 새 정보를 추가합니다.
class Employee(Person):
    def __init__(self, id, name, skill):
        super().__init__(id, name)   # Person 클래스의 생성자를 먼저 실행합니다.
        self.skill = skill           # 직원의 기술을 저장합니다.

    # 자기 정보와 기술까지 함께 출력합니다.
    def printInfo(self):
        super().printInfo()          # Person의 printInfo를 먼저 실행합니다.
        print(f"Skill: {self.skill}")


# 아래 코드는 프로그램이 실행될 때 실제로 동작하는 부분입니다.
if __name__ == "__main__":
    # 여러 사람 객체를 하나의 목록에 담아 관리합니다.
    people = [
        Person(1, "홍길동"),
        Person(2, "이순신"),
        Manager(3, "김철수", "팀장"),
        Manager(4, "박영희", "부장"),
        Employee(5, "최민수", "Python"),
        Employee(6, "정다은", "Java"),
        Employee(7, "윤서준", "C++"),
        Manager(8, "오지혜", "과장"),
        Employee(9, "한유진", "SQL"),
        Employee(10, "강태호", "HTML"),
    ]

    # 저장된 객체들의 정보를 하나씩 출력합니다.
    print("=== 인스턴스 정보 ===")
    for person in people:
        person.printInfo()      # 각 객체마다 자기 방식으로 정보를 출력합니다.
        print("-" * 20)
