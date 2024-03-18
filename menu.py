import rich
import os  #


#Menu class to be inherited by main menu and all submenus
class Menu():
  #paramaters include menu items, the queue to which tasks that require fetching from an api are added to, the name of the class (passed to __repr__)
  def __init__(self, choices, queue, classname):
    self.choices = choices
    self.classname = classname
    self.que = queue
    self.border = "________________"

  def __repr__(self):
    return self.classname

  def run(self):
    while True:
      self.display_menu()
      self.choice = input()
      print(
          end="\033c"
      )  #Dennis Rasulev from StackOverflow: "How can I clear the interpreter console?"
      action = self.choices.get(self.choice)
      if self.choice == self.exit:
        break
      if action:
        action[1]()
      else:
        rich.print(
            f"[yellow2]'{self.choice}' is an invalid option.[/yellow2] [italic]please try again[/]"
        )

  def addfunctoq(self, func):
    self.que.put(func)

  def output(self, output):
    print(self.border)
    rich.print(f"[b]OUTPUT:[/]\n\n {output}\n")
    print(self.border)

  def display_menu(self):
    print(self.border)
    rich.print(f"\n     [green b]{self}[/]\n")
    for menukey, menuitem in self.choices.items():
      rich.print(f"[blue bold]{menukey}:[/] [cyan]{menuitem[0]}[/]")
    if self.__class__.__name__ == "MainMenu":
      self.exit = "q"
      rich.print("[red][b]q:[/] exit[/]\n")
    else:
      self.exit = "b"
      rich.print("[magenta][b]b:[/] back[/]\n")
    print("________________")
    rich.print("\n[italic]please enter a menu option:[/]")
