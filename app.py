import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app)

# creating disctionary may be for users.. check later 
# blog_post = {
#     'title': "Learning Python", 
#     'content': "What do they got in there? King Kong? Must go faster. Yeah, but John, if The Pirates of the Caribbean breaks down, the pirates don’t eat the tourists. We gotta burn the rain forest, dump toxic waste, pollute the air, and rip up the OZONE! 'Cause maybe if we screw up this planet enough, they won't want it anymore! Must go faster... go, go, go, go, go! You really think you can fly that thing? God help us, we're in the hands of engineers. Yeah, but John, if The Pirates of the Caribbean breaks down, th pirates don’t eat the tourists. You know what? It is beets. I've crashed into a beet truck.Yeah, but John, if The Pirates of the Caribbean breaks down, the pirates don’t eat the tourists. We gotta burn the rain forest, dump toxic waste, pollu the air, and rip up the OZONE! 'Cause maybe if we screw up this planet enough, they won't want it anymore! ",
#     'username': "Jeff Goldblum",
#     'hashtags': ['#jef', '#goldmember']
# }
# print(blog_post.get("title"))

def get_loginToken(length):
    password_characters = string.ascii_letters + string.digits
    login_token = ''.join(random.choice(password_characters) for i in range(length))
    return login_token

@app.route('/api/login', methods=['POST', 'DELETE'])
def login():
    if request.method == 'POST':
        conn = None
        cursor = None
        userEmail = request.json.get("email")
        userPassword = request.json.get("password")
        rows = None
        user = None
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email=? and password=?", [userEmail, userPassword])
            user = cursor.fetchall()
            rows = cursor.rowcount
            if (rows == 1):
                loginToken = get_loginToken(30)
                print(loginToken)
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?,?)", [user[0][0], loginToken])
                conn.commit()
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Successfully Logged in..", mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong!", mimetype = "text/html", status = 500)

    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        userId = request.json.get("id")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("DELETE FROM user_session WHERE loginToken=?", [loginToken])
            conn.commit()
            rows = cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)        
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Successfully Logged out!", mimetype = "text/html", status = 201)
            else:
                return Response("Something went wrong... please try again", mimetype = "text/html", status = 500)


@app.route('/api/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def users():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        users_data={}
        user_id = request.json.get("id")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if user_id == None and user_Id == "":
                cursor.execute("SELECT * FROM user WHERE id=?", [user_id,])
            else:
                cursor.execute("SELECT * FROM user")
            rows = cursor.fetchall()
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows):
                users=[]
                for row in rows:
                    users_data={
                        "userId": row[0],
                        "email" : row[1],
                        "username": row[2],
                        "bio": row[4],
                        "birthdate" : row[5]
                    }
                    users.append(users_data)
                return Response(json.dumps(users, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
                # Ask ALEX about the data to be returned and check the array as discussed with jose 
    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        user_information={}
        userEmail = request.json.get("email")
        userName = request.json.get("username")
        userPassword = request.json.get("password")
        userBio = request.json.get("bio")
        userBirthdate = request.json.get("birthdate")
       
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("INSERT INTO user(email, username, password, bio, birthdate) VALUES (?,?,?,?,?)", [userEmail, userName, userPassword, userBio, userBirthdate, ])
            user_id = cursor.lastrowid
            rows = cursor.rowcount
            if rows == 1:
                loginToken = get_loginToken(30)
                print(loginToken)
                # ask Alex about the last rows inserted user_id = cursor.lastrowid
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?,?)", [user_id, loginToken])
                conn.commit()
                rows = cursor.rowcount
                print(rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                user_information = {
                    "email": userEmail,
                    "username": userName,
                    "password": userPassword,
                    "bio": userBio,
                    "birthdate": userBirthdate,
                    "userId": user_id,
                    "loginToken": loginToken
                }
                return Response(json.dumps(user_information, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        user = None
        users_data={}
        userEmail = request.json.get("email")
        userName = request.json.get("username")
        userPassword = request.json.get("password")
        userBio = request.json.get("bio")
        userBirthdate = request.json.get("birthdate")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken = ?",[loginToken,])
            user_update = cursor.fetchone()
            print(user_update)
            if user_update:
                if (userEmail != "" and userEmail != None):
                    cursor.execute("UPDATE user SET email = ? WHERE id = ?", [userEmail, user_update[0],])
                if (userName != "" and userName != None):
                    cursor.execute("UPDATE user SET username = ? WHERE id = ?", [userName, user_update[0],])
                if (userPassword != "" and userPassword != None):
                    cursor.execute("UPDATE user SET password = ? WHERE id = ?", [userPassword, user_update[0],])
                if (userBio != "" and userBio != None):
                    cursor.execute("UPDATE user SET bio = ? WHERE id = ?", [userBio, user_update[0],])
                if (userBirthdate != "" and userBirthdate != None):
                    cursor.execute("UPDATE user SET birthdate = ? WHERE id = ?", [userBirthdate, user_update[0]],)
                conn.commit()
                rows = cursor.rowcount
                cursor.execute("SELECT * FROM user WHERE id=?", [user_update[0],])
                user = cursor.fetchall()
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
                # check with ALEX ERROR
            if(rows != None): 
                users_data={
                        "userId": user_update[0],
                        "email" : user[0][1],
                        "username": user[0][2],
                        "bio": user[0][3],
                        "birthdate" : user[0][4],
                    } 
                return Response(json.dumps(users_data, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)           
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        userPassword = request.json.get("password")
        loginToken = request.json.get("loginToken")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("DELETE FROM user eWHERE loginToken = ?",[loginToken,])
            conn.commit()        
            rows= cursor.rowcount      
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows != None):
                return Response("Account deleted!", mimetype = "text/html", status = 204)
            else:
                return Response("Error occured while deleting your account...", mimetype = "text/html", status = 500)

@app.route('/api/tweets', methods=[ 'GET','POST', 'DELETE','PATCH'])
# Get tweets from user or a specific user 
def tweets():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        tweets_info=[]
        tweet_dict={}
        user_id = request.args.get("userId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if user_id == None and user_Id == "":
                cursor.execute("SELECT t.id, t.userId, t.content, t.createdAt, u.username FROM tweet t INNER JOIN user u ON t.userId = u.id")
            else:
                cursor.execute("SELECT t.id, t.userId, t.content, t.createdAt, u.username FROM tweet t INNER JOIN user u ON t.userId = u.id WHERE u.id=?", [user_id],)
            rows = cursor.fetchall()
            print (rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows!= None):
                users=[]
                for row in rows:
                    tweet_dict={
                        "tweetId": row[0],
                        "userId" : row[1],
                        "content": row[2],
                        "createdAt" : row[3],
                        "username": row[4]
                    }
                    tweets_info.append(tweet_dict)
                return Response(json.dumps(tweets_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # create a new tweet for a user
    # ASK ALEX about the doctionary date and local data for user name and so.. 
    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        tweetId=None
        createdAt=None
        tweet_info={}
        loginToken = request.json.get("loginToken")
        tweet_content = request.json.get("content")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()           
            cursor.execute("SELECT * FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            if user !=None:
                cursor.execute("INSERT INTO tweet(userId, content) VALUES(?,?)", [user[0][0],tweet_content, ])
                conn.commit()
                rows= cursor.rowcount      
                print (tweetId)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows==1):
                tweet_info={
                    "tweetId": tweetId,
                    "userId" : user[0][0] ,
                    "content": tweet_content,
                    "createdAt" :createdAt ,
                    "username": user[0][1],
                    }
                return Response(json.dumps(tweet_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        updated_tweet = None
        user=None
        updatedtweet_info={}
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")
        tweet_content = request.json.get("content")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()

            cursor.execute("SELECT * FROM user_session WHERE loginToken =? ", [loginToken,])
            user=cursor.fetchall()

            cursor.execute("UPDATE tweet SET content = ? WHERE id=? AND userId=?", [tweet_content,tweetId,user[0][0] ])
            conn.commit()
            rows = cursor.rowcount
            # cursor.execute("SELECT * FROM tweet WHERE id=?", [tweetId,)
            # updated_tweet = cursor.fetchall()
            # print(updated_tweet)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                updatedtweet_info={
                    "tweetId": tweetId,
                    "content": tweet_content,
                    }
              
                return Response(json.dumps(updatedtweet_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM tweet WHERE id=? AND userId=?", [tweetId,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response(json.dumps("Deleted successfully", default=str), mimetype="application/json", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
@app.route('/api/comments', methods=[ 'GET', 'POST', 'PATCH', 'DELETE'])
def comments():
    if request.method == 'GET':
        conn = None
        cursor = None
        rows = None
        comments_info=[]
        comment_dict={}
        tweet_Id = request.args.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            if tweet_Id == None and tweet_Id == "":
                cursor.execute("SELECT * FROM comment c INNER JOIN tweet t ON c.tweetId = t.id")
            else:
                cursor.execute("SELECT * FROM comment c INNER JOIN tweet t ON c.tweetId = t.id WHERE tweetId=?", [tweet_Id],)
            rows = cursor.fetchall()
            print (rows)
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows!= None):
                tweets=[]
                for row in rows:
                    comments_dict={
                        "commentId": row[0],
                        "tweetId" : row[1],
                        "userId": row[2],
                        "content": row[3],
                        "createdAt" : row[4],
                        "username": row[5]
                    }
                    comments_info.append(comments_dict)
                return Response(json.dumps(comments_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        createdAt=None
        comments_info={}
        loginToken = request.json.get("loginToken")
        content = request.json.get("content")
        tweet_Id = request.json.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()           
            cursor.execute("SELECT * FROM user_session WHERE loginToken =?", [loginToken,])
            user=cursor.fetchall()
            print(user)
            if user !=None:
                cursor.execute("INSERT INTO comment(tweetId, userId, content) VALUES(?,?,?)", [tweet_Id,user[0][2],content, ])
                conn.commit()
                rows= cursor.rowcount
                cursor.execute("SELECT c.id, c.tweetId, c.userId, c.content, c.createdAt, u.username FROM user u INNER JOIN comment c ON u.id = c.userId WHERE c.tweetId = ?",[tweet_Id, ] )
                user=cursor.fetchall()
      
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows==1):
                comments_info={
                    "commentId": user[0][0],
                    "tweetId": tweet_Id,
                    "userId" : user[0][1] ,
                    "username":user[0][5] ,
                    "content": content,
                    "createdAt" :createdAt ,
                    }
                return Response(json.dumps(comments_info, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    # elif request.method == 'PATCH':
    #     conn = None
    #     cursor = None
    #     rows = None
    #     updated_comment = None
    #     user=None
    #     updatedcomment_info={}
    #     loginToken = request.json.get("loginToken")
    #     comment_Id = request.json.get("id")
    #     comment_content = request.json.get("content")
    #     try:
    #         conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
    #         cursor=conn.cursor()

    #         cursor.execute("SELECT * FROM user_session WHERE loginToken =? ", [loginToken,])
    #         user=cursor.fetchall()

    #         cursor.execute("UPDATE comment SET content = ? WHERE id=? AND userId=?", [comment_content,comment_Id,user[0][0] ])
    #         conn.commit()
    #         rows = cursor.rowcount
            
    #         cursor.execute("SELECT * FROM comment WHERE id=?", [comment_Id,])
    #         updated_comment=cursor.fetchall()
    #         print(updated_comment)

    #     except mariadb.ProgrammingError as error:
    #             print("Programming Error.. ")
    #             print(error)
    #     except mariadb.DatabaseError as error:
    #             print("Database Error...")
    #             print(error)
    #     except mariadb.OperationalError as error:
    #             print("Connection Error...")
    #             print(error)
    #     except Exception as error:
    #             print("This is a general error to be checked! ")
    #             print(error)
    #     finally:
    #         if(cursor != None):
    #             cursor.close()
    #         if(conn != None):
    #             conn.rollback()
    #             conn.close()
    #         if(rows == 1):
    #             updatedcomment_info={
    #                 "commentId": comment_Id,
    #                 "tweetId": ,
    #                 "userId": ,
    #                 "username": ,
    #                 "content": comment_content,
    #                 "createdAt": 
    #                 }
              
    #             return Response(json.dumps(updatedcomment_info, default=str), mimetype="application/json", status=200)
    #         else:
    #             return Response("Something went wrong!", mimetype="text/html", status=500)
                
                # update it to comment

    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        user = None
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken=?", [loginToken,])
            user = cursor.fetchone()
            print(user)
            if user !=None:
                cursor.execute("DELETE FROM tweet WHERE id=? AND userId=?", [tweetId,user[0],])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
                print("Programming Error.. ")
                print(error)
        except mariadb.DatabaseError as error:
                print("Database Error...")
                print(error)
        except mariadb.OperationalError as error:
                print("Connection Error...")
                print(error)
        except Exception as error:
                print("This is a general error to be checked! ")
                print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):           
                return Response(json.dumps("Deleted successfully", default=str), mimetype="application/json", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)








# @app.route('/api/follows', methods=[ 'POST', 'POST','DELETE'])

# @app.route('/api/followers', methods=[ 'GET'])


# @app.route('/api/tweet-likes', methods=[ 'GET', 'POST', 'DELETE'])

# @app.route('/api/comments', methods=[ 'GET', 'POST', 'PATCH', 'DELETE'])
# @app.route('/api/comment-likes', methods=[ 'GET', 'POST', 'DELETE'])