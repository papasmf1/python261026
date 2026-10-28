"""
사람들을 소개하는 놀이 나라 이야기예요!

이 파일에는 세 종류의 친구가 나와요.
  1. Person   : 그냥 "사람" 친구예요. 번호표와 이름이 있어요.
  2. Manager  : "대장님" 친구예요. 사람인데 직함(대장, 반장 같은 것)도 있어요.
  3. Employee : "일꾼" 친구예요. 사람인데 잘하는 재주(기술)도 있어요.
"""


class Person:
    """
    '사람' 친구를 만드는 설계도(클래스)예요.

    붕어빵 틀을 생각해 보세요. 틀은 하나지만 붕어빵은 여러 개 만들 수 있죠?
    Person 설계도로도 사람을 여러 명 만들 수 있어요.

    모든 사람은 이런 것을 가지고 있어요:
        id   : 번호표예요. (예: 유치원 출석 번호 1번)
        name : 이름이에요. (예: "철수")
    """

    def __init__(self, id, name):
        """
        사람이 처음 태어날 때(만들어질 때) 딱 한 번 불리는 함수예요.

        인자(받는 것):
            id   : 이 사람의 번호표
            name : 이 사람의 이름

        받은 번호표와 이름을 내 몸(self)에 꼭꼭 붙여서 기억해 둬요.
        """
        self.id = id
        self.name = name

    def printInfo(self):
        """
        "안녕, 나는 이런 사람이야!" 하고 자기소개를 말해요(화면에 출력).

        예: ID: 1, Name: 철수
        """
        print(f"ID: {self.id}, Name: {self.name}")


class Manager(Person):
    """
    '대장님' 친구를 만드는 설계도예요.

    Person(사람)을 물려받았어요(상속). 엄마 아빠에게 눈, 코, 입을 물려받는 것처럼
    번호표(id)와 이름(name), 자기소개(printInfo)를 그대로 가지고 있어요.

    거기에 새로운 것을 하나 더 가져요:
        title : 직함이에요. (예: "반장", "팀장")
    """

    def __init__(self, id, name, title):
        """
        대장님이 만들어질 때 불리는 함수예요.

        인자(받는 것):
            id    : 번호표
            name  : 이름
            title : 직함

        번호표와 이름은 부모님(Person)에게 맡기고(super),
        직함은 대장님이 직접 기억해요.
        """
        super().__init__(id, name)
        self.title = title

    def printInfo(self):
        """
        대장님의 자기소개예요.

        먼저 부모님(Person)의 자기소개(번호표, 이름)를 말하고,
        그다음 줄에 내 직함을 말해요.

        예:
            ID: 2, Name: 영희
            Title: 반장
        """
        super().printInfo()
        print(f"Title: {self.title}")


class Employee(Person):
    """
    '일꾼' 친구를 만드는 설계도예요.

    Person(사람)을 물려받았어요(상속). 그래서 번호표(id)와 이름(name)이 있어요.

    거기에 새로운 것을 하나 더 가져요:
        skill : 잘하는 재주예요. (예: "그림 그리기", "Python")
    """

    def __init__(self, id, name, skill):
        """
        일꾼이 만들어질 때 불리는 함수예요.

        인자(받는 것):
            id    : 번호표
            name  : 이름
            skill : 잘하는 재주

        번호표와 이름은 부모님(Person)에게 맡기고(super),
        재주는 일꾼이 직접 기억해요.
        """
        super().__init__(id, name)
        self.skill = skill

    def printInfo(self):
        """
        일꾼의 자기소개예요.

        먼저 부모님(Person)의 자기소개(번호표, 이름)를 말하고,
        그다음 줄에 내가 잘하는 재주를 말해요.

        예:
            ID: 3, Name: 민수
            Skill: Python
        """
        super().printInfo()
        print(f"Skill: {self.skill}")


#인스턴스 생성
p1 = Person(100, "전우치")
p1.printInfo()

m1 = Manager(101, "이순신", "팀장")
m1.printInfo()

e1 = Employee(102, "홍길동", "Python")
e1.printInfo()