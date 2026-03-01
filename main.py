from pathlib import Path
import json
import random 
import string


class Bank:
    database = "data.json"
    data = []

    try :
        if Path(database).exists():
            
            with open(database ,'r') as f:
                data = json.loads(f.read())
                
        else:
            print("No such file exists..")

            
    except Exception as e:
        # print("Error occured ..")
        pass

    @classmethod
    def update(cls):
            with open (Bank.database ,'w') as f:
                f.write(json.dumps(cls.data))
    @staticmethod
    def generateAcc():
         digits = random.choices(string.digits , k = 4)
         alpha = random.choices(string.ascii_letters, k = 4)
         id = digits + alpha
         
         return "".join(id)
    

    def createAccount(self):
            info = {
                'name' : input("Enter your name :- "),
                'age'  : int(input("Enter your age :- ")),
                'email' : input("Enter your email address : "),
                'phone_number' : int(input("Enter your phone number")),
                'pin'  : int(input("Enter your pin : ")) ,
                'accountno' : Bank.generateAcc(),
                'balance' : 0
            }

            if info['age'] >= 18 and len(str(info['pin'])) == 4  and len(str(info['phone_number'])) == 10 :
            
        
                Bank.data.append(info)
                Bank.update()
                print('Data added in list')
            
            # elif Bank.data.accounno ==  anj:

            else:
                print('Credential are not valid! ')

    def depositmoney(self):
         accountno = input("Enter your amount no. : ")
         pin = input("Enter your 4 digit pin . : ")

         user_data = [ i for i in Bank.data if i[0]["accountno"] == accountno and ["pin"] == pin]
         if user_data == False :
              print("User not Found ")
         else:
              amount  = int(input("paise :- "))
              if amount <= 0:
                   print("Invalid amount ")
              elif amount > 10000:
                   print("Greater then 10000")
              else:
                   user_data[0]["balance"] += amount 
                   Bank.update()
                   print("Amount Creadited")


    def withdrawmoney(self):
        accountno = input("Enter your account no: ")
        pin = int(input("Enter your pin: "))

        user_data = [i for i in Bank.data if i["Account_no."] == accountno and  i["Pin"]==pin]
        if user_data == False:
            print("User not found! ")

        else:
            amount = int(input("Enter how much money you want to deposit : "))
            if amount <= 0:
                print("Invalid amount ")

            elif amount > 10000:
                print("Amount acceed from limit ")

            else:
                if user_data[0]["Balance"] < amount:
                    print("Insufficient Funds...")
                else:
                    user_data[0]["Balance"] -= amount
                Bank.update()
                print("Amount dbedited ")

            
    def details(self):
         accountno = input("Enter your account no :")
         pin = input("Enter your 4 digit no  :")

         user_data = [i for i in Bank.data if i [0]["accountno"] == accountno and i["pin"] == pin]
         if user_data  == False:
              print("User not Found !")
         else:
              for i in user_data[0]:
                   
                   print(i , user_data[0][i])
                   

    def delete(self):
        accountno = input("Enter your account no :")
        pin = input("Enter your pin no :")

        user_data = [i for i in Bank.data if i ["Account_no"] == accountno and i["pin"] == pin]
        if user_data == False:
            print("No such user exists ")
        else:
            print("Are you sure you want to delete your account ? (yes/no)")

            choice = input()
            if choice == "yes":
                ind = Bank.data.index(user_data[0])
                Bank.data.pop(ind)
                Bank.update()
                print("Account deleted successfully ")
            else:
                print("Operation Terminates")


    def update(self):
        accountno = input("Enter your account no: ")
        pin = int(input("Enter your pin: "))

        user_data = [i for i in Bank.data if i["Account_no."] == accountno and  i["Pin"]==pin]
        if user_data == False:
            print("No such user exists ")
        else:
            print("You can not change Account no. and Balance")
            print('Enter your details to update or just to press enter to skip them')

        new_data = {
            'Name':input("Enter your name: "),
            'Email':input("Enter your email: "),
            'PhoneNumber':int(input("Enter your number: ")),
            'Pin':int(input("Tell your new pin"))
            
        }
        if new_data['Name'] == "":
            new_data['Name'] = user_data[0]['Name']

        if new_data['Email'] == "":
            new_data['Email'] = user_data[0]['Email']

        if new_data['PhoneNumber'] == "":
            new_data['PhoneNumber'] = user_data[0]['PhoneNumber']

        if new_data['Pin'] == "":
            new_data['Pin'] = user_data[0]['Pin']

        new_data["name"] = user_data[0][""] 
        new_data[""] = user_data[0]["Account_no"] 


        for i in new_data :
             if new_data[i] == user_data[0][i]:
                  continue
             else:
                  user_data[0][i] = new_data[i]
        Bank.__update()
     

obj = Bank()
obj.createAccount()
obj.depositmoney()
obj.withdrawmoney()

obj.details()


print("Press 1 for creating an account :")
print("Press 2 for depositing money :")
print("Press 3 for withdrawning money :")
print("Press 4 for Account details :")
print("Press 5 for updating account details :")
print("Press 6 for deleting Account :")

choice = int(input("Enter your quieries :"))

if choice == 1:
     obj.createAccount()
elif choice == 2:
     obj.depositmoney()
elif choice == 3:
     obj.withdrawmoney()
elif choice == 4:
     obj.details()
elif choice == 5:
     obj.update()










