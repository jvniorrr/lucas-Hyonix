from discord import user
import pymongo
from pymongo import MongoClient
from pymongo import collection
import requests, os
from dotenv import load_dotenv
import hyonix

load_dotenv(os.path.join(os.getcwd(), ".env"))

class Database:
    def __init__(self, user, password) -> None:
        
        self.USER = user
        self.PASSWORD = password
        # self.USER = os.getenv("MONGO_USER")
        # self.PASSWORD = os.getenv("MONGO_PASSWORD")

        self.CONNECTION_STRING = f"mongodb+srv://root:{self.PASSWORD}@testcluster.rdbs1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

        

        #  to add to db
        # post = {"_id":0, "name":"tim", "score":5}
        # collection.insert_one(post)
    def returnCollection(self):
        #  this is the actual connect / cursor object
        cluster = MongoClient(self.CONNECTION_STRING)

        #  retrieve the actual database
        db = cluster["test"]

        collection = db["test"]

        try:
            collection.create_index("discord_id", unique=True, background=True)

        except Exception as e:
            print("Index has already been created.")

        return collection

    def entry(self, user_name, user_id, server_ref):
        """Method for entering a new entry to DB.
        
        Parameters
        -----------
        user_name : str
            - discord username associated with the user
        user_id : int
            - integer value associated with discord user
        server_ref : dict
            - dict value to reference the server
            
        """        

        collection = self.returnCollection()

        #  retrieve information from HYONIX API and format it 
        user = { 
            "name":user_name,
            "discord_id":user_id,
            "servers": list(server_ref)
        }
        

        # enter user to DB if not stored already
        try:
            collection.insert_one(user)
            # succesfully inserted a new entry
            return True
            
        except Exception as e:
            print("User is already stored", e)
            return False


    def checkCurrentUser(self, discord_id):
        """
        Method to return server information of said IP.

        Parameters
        ----------
        server_ref : str
            - text value to reference the server"""

        collection = self.returnCollection()

        try:
            currentUser = collection.find_one({"discord_id":discord_id})

            if currentUser != None:
                return True
            else:
                return False

        except Exception as e:
            print("Error occured checking users status.", e)
            return False

    def updateUser(self, discord_id, server_ref):
        collection = self.returnCollection()

        try:
            collection.update_one({"discord_id":discord_id}, {'$push': {"servers":server_ref}})
            return True
        except Exception as e:
            print("Error occured updating the Users information.", e)
            return False

    def returnUserInformation(self, discord_id) -> dict or None:
        """Method to return users current stored information
        
        Parameters
        ---------
        discord_id : int
            - int value associated with discord member"""
        collection = self.returnCollection()

        userInfo = None

        try:
            currentUser = collection.find_one({"discord_id":discord_id})

            return currentUser
        except Exception as e:
            print("Error occured retrieving the users information.")
            return userInfo

    def removeUser(self, discord_id) -> bool:
        """Method to remove the User from the DB
        
        Parameters
        ---------
        discord_id : int
            - int value associated with discord member"""

        collection = self.returnCollection()
        deleted = False
        # delete user entry
        try:
            deleted = collection.delete_one({"discord_id":discord_id})
            if deleted.deleted_count == 1:
                deleted = True
                # return deleted
        except Exception as e:
            print("Error occured removing user from DB.", e)
            
        finally:
            return deleted
            



if __name__ == "__main__":
    b = Database().entry('junior', '567890', '192.168.1.1')
        