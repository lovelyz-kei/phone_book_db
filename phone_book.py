import cx_Oracle as cxo
import re

class phoneBook:
	def __init__(self):
		self.connection = None
		self.cursor = None

	def connectOracle(self, id, pwd, ip, port, dbName):
		dsn = cxo.makedsn(ip, port, dbName)
		self.connection = cxo.connect(id, pwd, dsn)
		self.cursor = self.connection.cursor();

	def closeOracle(self):
		self.connection.close()

	
	def selectMenu(self):
		print("\n=== 연락처 프로그램 ===")
		print("1. 연락처 등록")
		print("2. 연락처 검색(수정 및 삭제)")
		print("3. 연락처 전체 보기")
		print("4. 연락처 그룹별 보기")
		print("0. 프로그램 종료")
		print("메뉴 선택 : ")
		return input()

	def insertNewPhone(self):
		print("\n=== 1. 연락처 등록 ===")
		insertName = ""
		insertEmail = ""
		insertGroup = ""
		groupName = ""
		insertPhoneList = []

		# 이름 입력 받기
		while True:
			print("* 이름을 입력하세요(특수문자는 입력할 수 없습니다. 최대 40자) : ")
			insertName = input()

			namePattern = re.compile('^[a-zA-Z가-힣0-9]*$')
			isMatch = namePattern.match(insertName)

			if isMatch == None:
				print("\n이름에는 특수문자를 넣을 수 없습니다.")
				print("올바르게 다시 입력해 주세요.\n")
				continue
			
			if len(insertName) > 40:
				print("\n이름은 40자를 넘을 수 없습니다.")
				print("올바르게 다시 입력해 주세요.\n")
				continue
			break

		# 이메일 입력 받기
		while True:
			print("* 이메일을 입력하세요(이메일 형식에 맞게 입력하세요. 최대 40자)")
			insertEmail = input()

			emailPattern = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
			isMatch = emailPattern.match(insertEmail)

			if isMatch == None:
				print("\n이메일 형식에 맞도록 올바르게 다시 입력해 주세요.\n")
				continue
			if len(insertEmail) > 40:
				print("\n이메일은 40자를 넘을 수 없습니다.")
				print("올바르게 다시 입력해 주세요.\n")
				continue

			self.cursor.execute("SELECT count(*) FROM user_main WHERE e_mail = :1", (insertEmail, ))

			alreadyExistEmail = self.cursor.fetchone()

			if alreadyExistEmail[0] != 0:
				print("\n입력하신 이메일 " + insertEmail + "은 이미 존재합니다.")
				print("전화 번호부에 없는 이메일을 입력해 주세요.")
				continue
			break

		# 그룹 목록 가져오기
		self.cursor.execute(
			"""SELECT group_id, group_name FROM group_info
			ORDER BY group_id""")	
		groupList = self.cursor.fetchall()

		# 그룹 입력 받기
		while True:
			print("\n === 그룹 목록 ===")
			for groupItem in groupList:
				print(groupItem[0], groupItem[1])

			print("그룹 번호 선택(그룹 추가 시 0 입력) : ")
			insertGroup = input()

			if insertGroup == 0:
				while True:
					print("추가할 그룹 이름 입력(최대 40자) : ")
					insertGroupName = input()

					if len(insertGroupName) > 40:
						print("\n그룹 이름은 40자를 넘을 수 없습니다.")
						print("올바르게 다시 입력해 주세요.\n")
						continue
					continue

				self.connection.begin()
				self.cursor.execute(
					"""INSERT INTO group_info 
					VALUES((SELECT NVL(MAX(group_id),0)+1 FROM group_info), :1)"""
					, (insertGroupName,))
				self.connection.commit()
			else:
				existsGroup = False

				for groupItem in groupList:
					if insertGroup == groupItem[0]:
						existsGroup = True
						groupName = groupItem[1]
						break

				if not existsGroup:
					print("\n입력한 그룹 번호는 존재하지 않습니다.")
					print("그룹 목록에 존재하는 번호를 올바르게 입력해 주세요.\n")
					continue

			break

		# 전화 번호 입력 받기
		while True:
			print("* 번호를 입력하세요(-을 제외한 숫자만 입력하세요. 최대 11자)")
			insertPhone = input()
			gubunName = ""

			phonePattern = re.compile('^[0-9]*$')
			isMatch = phonePattern.match(insertPhone)

			if isMatch == None:
				print("\n전화 번호에는 숫자만 입력해주세요.")
				print("올바르게 다시 입력해 주세요.\n")
				continue

			if len(insertPhone) > 11:
				print("\n전화 번호는 11자를 넘을 수 없습니다.")
				print("올바르게 다시 입력해 주세요.\n")
				continue

			self.cursor.execute("SELECT count(*) as cnt FROM num_info WHERE phone_num = " + insertPhone)

			alreadyExistNum = self.cursor.fetchone()

			if alreadyExistNum[0] != 0:
				print("\n입력하신 번호 " + insertPhone + "은 이미 존재합니다.")
				print("전화 번호부에 없는 번호를 입력해 주세요.")
				continue

			self.cursor.execute(
					"""SELECT gubun_id, gubun_name 
					FROM gubun_info""")

			gubunList = self.cursor.fetchall()

			# 전화 번호의 구분 번호 입력 받기
			while True:
				print("== 번호 구분 목록 ==")
				for row in gubunList:
					print(row[0], row[1])
				print("입력한 번호의 구분을 선택하세요 : ")
				gubunSel = input()

				existsGubun = False
				for row in gubunList:
					if gubunSel == row[0]:
						existsGubun = True
						gubunName = row[1]
						break

				if not existsGubun:
					print("\n입력한 구분 번호는 존재하지 않습니다.")
					print("구분 목록에 존재하는 번호를 올바르게 입력해 주세요.")
					continue
				break

			insertPhoneList.append({"phoneNum": insertPhone, "gubunId":gubunSel, "gubunName":gubunName})
			print("\n번호가 임시 저장되었습니다.")

			addExtraNum = False
			while(True):
				print("번호를 추가로 저장하시겠습니까? (y/n)")
				choiceForExtraNum = input()
				if choiceForExtraNum == "y":
					addExtraNum = True
					break
				elif choiceForExtraNum == "n":
					break
				else:
					print("\ny와 n만을 입력해 주세요.\n")
					continue

			if(addExtraNum):
				continue

			break

		print("\n등록하신 전화 번호 정보를 데이터베이스에 저장 중입니다.")
		print("잠시만 기다려 주세요...")

		self.connection.begin()
		self.cursor.execute(
			"""INSERT INTO user_main 
			VALUES((SELECT NVL(MAX(user_id), 0)+1 FROM user_main), :1, :2, :3)"""
			, (insertName, insertGroup, insertEmail))

		for phoneItem in insertPhoneList:
			self.cursor.execute(
				"""INSERT INTO num_info 
				VALUES( :1, (SELECT NVL(MAX(user_id), 1) FROM user_main), :2)"""
				, (phoneItem["phoneNum"], phoneItem["gubunId"]))

		self.connection.commit()

		print("\n전화 번호 등록이 완료되었습니다.")
		print("등록하신 전화 번호 내용은 다음과 같습니다.")

		print("이름 : " + insertName)
		print("이메일 : " + insertEmail)
		print("그룹 : " + groupName)
		print("번호 목록 : ")
		for phoneItem in insertPhoneList:
			print(phoneItem["phoneNum"] + "(" + phoneItem["gubunName"] + ")")

		print("\n메인 메뉴로 돌아갑니다.")

	def searchPhone(self):
		print("\n=== 2. 연락처 검색(수정 및 삭제) ===\n")
		print("1. 이름으로 검색")
		print("2. 번호로 검색")
		print("메뉴 선택 : ")
		
		searchSel = input()

		if searchSel == "1":
			self.searchByName()
		elif searchSel == "2":
			self.searchByPhone()
		else:
			print("잘못된 번호를 입력했습니다.")

		print("\n메인 메뉴로 돌아갑니다.")

	def searchByName(self):
		print("\n === 이름으로 검색 ===")
		print("검색할 이름 입력 : ")
		nameForSearch = input()

		self.cursor.execute("""SELECT u.user_id, u.user_name, u.group_id, u.e_mail, g.group_name, n.phone_num, gb.gubun_name
			FROM user_main u, num_info n, group_info g, gubun_info gb
			WHERE u.user_id=n.user_id AND u.group_id=g.group_id AND n.gubun_id=gb.gubun_id 
			AND u.user_name like '%""" + nameForSearch + """%' 
			ORDER BY u.user_id""")

		searchResult = self.cursor.fetchall()

		if len(searchResult) == 0:
			print("\n해당하는 이름이 전화번호부에 없습니다.")
			return

		preUserId = 0;
		print("\n*** 검색 결과 ***")
		for row in searchResult:
			'''
				row[0] : u.user_id
				row[1] : u.user_name
				row[2] : u.group_id
				row[3] : u.e_mail
				row[4] : g.group_name
				row[5] : n.phone_num
				row[6] : gb.gubun_name
			'''
			if row[0] != preUserId:
				preUserId = row[0]
				print("ID : " + row[0])
				print("이름 : " + row[1])
				print("이메일 : " + row[3])
				print("그룹 이름 : " + row[4])
				print("번호 목록")

			print(row[5], row[6])

		print("\n*** 검색 후 작업 선택 ***")
		print("1. 수정")
		print("2. 삭제")
		print("3. 나가기")
		print("작업 번호 입력 : ")
		actionSel = input()

		if actionSel == "1":
			self.modifyItem(searchResult)
		elif actionSel == "2":
			self.deleteItem(searchResult)
		elif actionSel == "3":
			pass
		else:
			print("\n잘못된 번호를 입력했습니다.")

	def searchByPhone(self):
		print("\n === 전화 번호로 검색 ===")
		print("검색할 전화 번호 입력 : ")
		phoneForSearch = input()

		self.cursor.execute("SELECT NVL(user_id, 0) FROM num_info WHERE phone_num like '%" + phoneForSearch + "%'")

		userId = self.cursor.fetchone()

		if userId[0] == 0:
			print("\n입력하신 전화 번호는 전화번호부에 없습니다.")
			return

		self.cursor.execute("""SELECT u.user_id, u.user_name, u.group_id, u.e_mail, g.group_name, n.phone_num, gb.gubun_name
			FROM user_main u, num_info n, group_info g, gubun_info gb
			WHERE u.user_id=n.user_id AND u.group_id=g.group_id AND n.gubun_id=gb.gubun_id 
			AND u.user_id = """ + userId[0] + """ ORDER BY u.user_id""")

		searchResult = self.cursor.fetchall()

		preUserId = 0;
		print("\n*** 검색 결과 ***")
		for row in searchResult:
			'''
				row[0] : u.user_id
				row[1] : u.user_name
				row[2] : u.group_id
				row[3] : u.e_mail
				row[4] : g.group_name
				row[5] : n.phone_num
				row[6] : gb.gubun_name
			'''
			if row[0] != preUserId:
				preUserId = row[0]
				print("ID : " + row[0])
				print("이름 : " + row[1])
				print("이메일 : " + row[3])
				print("그룹 이름 : " + row[4])
				print("번호 목록")

			print(row[5], row[6])

		print("\n*** 검색 후 작업 선택 ***")
		print("1. 수정")
		print("2. 삭제")
		print("3. 나가기")
		print("작업 번호 입력 : ")
		actionSel = input()

		if actionSel == "1":
			self.modifyItem(searchResult)
		elif actionSel == "2":
			self.deleteItem(searchResult)
		elif actionSel == "3":
			pass
		else:
			print("\n잘못된 번호를 입력했습니다.")

	def modifyItem(self, searchResult):
		userIdToModify = ""
		phoneNumToModify = ""
		if len(searchResult) == 1:
			userIdToModify = searchResult[0][0]
			phoneNumToModify = searchResult[0][5]
			
		else:
			print("\n수정할 연락처 항목의 ID를 입력하세요 : ")
			userIdToModify = input()

			existsId = False

			for row in searchResult:
				if row[0] == userIdToModify:
					existsId = True
					phoneNumToModify = row[5]
					break

			if not existsId:
				print("\n입력하신 ID는 검색 결과에 존재하지 않습니다.")
				return

		print("\n*** 수정할 항목 선택 ***")
		print("1. 이름")
		print("2. 번호")
		print("3. 이메일")
		print("4. 그룹")
		print("항목 번호 입력 : ")
		itemForModify = input()

		if itemForModify == "1":
			self.modifyName(userIdToModify)	
		elif itemForModify == "2":
			self.modifyNumber(phoneNumToModify)
		elif itemForModify == "3":
			self.modifyEmail(userIdToModify)
		elif itemForModify == "4":
			self.modifyGroup(userIdToModify)
		else:
			print("\n잘못된 항목 번호입니다.")

	def modifyName(self, userIdToModify):
		print("\n*** 이름 수정 ***")
		nameToModify = ""
		while True: 
			print("* 수정할 이름 입력(특수 문자 입력 불가, 최대 40자) : ")
			nameToModify = input()

			namePattern = re.compile('^[a-zA-Z가-힣0-9]*$')
			isMatch = namePattern.match(nameToModify)

			if isMatch == None:
				print("\n이름에는 특수문자를 넣을 수 없습니다.")
				print("올바르게 다시 입력해 주세요.\n")
				continue

			if len(nameToModify) > 40:
				print("\n이름은 40자를 넘을 수 없습니다.")
				print("올바르게 다시 입력해 주세요.\n")
				continue
			break

		self.connection.begin()
		self.cursor.execute(
			"""UPDATE user_main 
			SET user_name = :1 
			WHERE user_id = :2"""
			, (nameToModify, userIdToModify))
		self.connection.commit()
		print("이름 수정을 완료했습니다.")

	def modifyNumber(self, phoneNumToModify):
		print("\n*** 번호 수정***")
		phoneToModify = ""
		while True:
			print("* 수정할 번호 입력(-을 제외한 숫자만 입력하세요. 최대 11자) : ")
			phoneToModify = input()
			gubunName = ""

			phonePattern = re.compile('^[0-9]*$')
			isMatch = phonePattern.match(phoneToModify)

			if isMatch == None:
				print("\n번호에는 숫자만 입력해주세요.")
				print("올바르게 다시 입력해 주세요.\n")
				continue

			if len(phoneToModify) > 11:
				print("\n전화 번호는 11자를 넘을 수 없습니다.")
				print("올바르게 다시 입력해 주세요.\n")
				continue

			self.cursor.execute("SELECT count(*) as cnt FROM num_info WHERE phone_num = " + phoneToModify)

			alreadyExistNum = self.cursor.fetchone()

			if alreadyExistNum[0] != 0:
				print("\n입력하신 번호 " + phoneToModify + "은 이미 존재합니다.")
				print("전화 번호부에 없는 번호를 입력해 주세요.")
				continue
			break

		self.connection.begin()
		self.cursor.execute(
			"""UPDATE num_info 
			SET phone_num = :1 
			WHERE phone_num = :2"""
			, (phoneToModify, phoneNumToModify))
		self.connection.commit()
		print("전화 번호 수정을 완료했습니다.")

	def modifyEmail(self, userIdToModify):
		print("\n*** 이메일 수정 ***")
		emailToModify = ""
		while True:
			print("* 수정할 이메일 입력(이메일 형식에 맞게 입력하세요. 최대 40자) :")
			emailToModify = input()

			emailPattern = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
			isMatch = emailPattern.match(emailToModify)

			if isMatch == None:
				print("\n이메일 형식에 맞도록 올바르게 다시 입력해 주세요.\n")
				continue
			if len(emailToModify) > 40:
				print("\n이메일은 40자를 넘을 수 없습니다.")
				print("올바르게 다시 입력해 주세요.\n")
				continue

			self.cursor.execute("SELECT count(*) FROM user_main WHERE e_mail = :1", (emailToModify, ))

			alreadyExistEmail = self.cursor.fetchone()

			if alreadyExistEmail[0] != 0:
				print("\n입력하신 이메일 " + emailToModify + "은 이미 존재합니다.")
				print("전화 번호부에 없는 이메일을 입력해 주세요.")
				continue
			break

		self.connection.begin()
		self.cursor.execute(
			"""UPDATE user_main 
			SET e_mail = :1 
			WHERE user_id = :2"""
			, (emailToModify, userIdToModify))
		self.connection.commit()
		print("이메일 수정을 완료했습니다.")

	def modifyGroup(self, userIdToModify):
		print("\n*** 그룹 수정***")
		groupToModify = ""
		# 그룹 목록 가져오기
		self.cursor.execute(
			"""SELECT group_id, group_name FROM group_info
			ORDER BY group_id""")	
		groupList = self.cursor.fetchall()

		# 그룹 입력 받기
		while True:
			print("\n *** 그룹 목록 ***")
			for groupItem in groupList:
				print(groupItem[0], groupItem[1])

			print("그룹 번호 선택(그룹 추가 시 0 입력) : ")
			groupToModify = input()

			if groupToModify == 0:
				while True:
					print("추가할 그룹 이름 입력(최대 40자) : ")
					insertGroupName = input()

					if len(insertGroupName) > 40:
						print("\n그룹 이름은 40자를 넘을 수 없습니다.")
						print("올바르게 다시 입력해 주세요.\n")
						continue
					continue

				self.connection.begin()
				self.cursor.execute(
					"""INSERT INTO group_info 
					VALUES((SELECT NVL(MAX(group_id),0)+1 FROM group_info), :1)"""
					, (insertGroupName,))
				self.connection.commit()
			else:
				existsGroup = False

				for groupItem in groupList:
					if groupToModify == groupItem[0]:
						existsGroup = True
						groupName = groupItem[1]
						break

				if not existsGroup:
					print("\n입력한 그룹 번호는 존재하지 않습니다.")
					print("그룹 목록에 존재하는 번호를 올바르게 입력해 주세요.\n")
					continue

			break

		self.connection.begin()
		self.cursor.execute(
			"""UPDATE user_main 
			SET group_id = :1 
			WHERE user_id = :2"""
			, (groupToModify, userIdToModify))
		self.connection.commit()
		print("그룹 수정을 완료했습니다.")

	def deleteItem(self, searchResult):
		userIdToDelete = ""
		nameToDelete = ""
		phoneNumToDelete = ""
		if len(searchResult) == 1:
			userIdToDelete = searchResult[0][0]
			nameToDelete = searchResult[0][1]
			phoneNumToDelete = searchResult[0][5]
			
		else:
			print("\n삭제할 연락처 항목의 ID를 입력하세요 : ")
			userIdToDelete = input()

			existsId = False

			for row in searchResult:
				if row[0] == userIdToDelete:
					existsId = True
					nameToDelete = row[1]
					phoneNumToDelete = row[5]
					break

			if not existsId:
				print("\n입력하신 ID는 검색 결과에 존재하지 않습니다.")
				return

		print("\n*** 삭제할 항목 선택 ***")
		print("1. '" + nameToDelete + "'의 모든 데이터 삭제")
		print("2. 번호 항목 하나 삭제")
		print("항목 번호 입력 : ")
		itemForDelete = input()

		if itemForDelete == "1":
			self.deleteAll(userIdToDelete)	
		elif itemForDelete == "2":
			self.deleteNum(phoneNumToDelete)
		else:
			print("\n잘못된 항목 번호입니다.")

	def deleteAll(self, userIdToDelete):
		self.connection.begin()
		self.cursor.execute("DELETE FROM user_main WHERE user_id = " + userIdToDelete)
		self.cursor.execute("DELETE FROM num_info WHERE user_id = " + userIdToDelete)
		self.connection.commit()
		print("요청한 데이터 삭제를 마쳤습니다.")

	def deleteNum(self, phoneNumToDelete):
		self.connection.begin()
		self.cursor.execute("DELETE FROM num_info WHERE user_id = " + phoneNumToDelete)
		self.connection.commit()
		print("요청한 데이터 삭제를 마쳤습니다.")

	def showAllPhoneList(self):
		print("\n === 3. 연락처 전체 보기 ===")
		self.cursor.execute("""SELECT u.user_id, u.user_name, u.group_id, u.e_mail, g.group_name, n.phone_num, gb.gubun_name 
			FROM user_main u, num_info n, group_info g, gubun_info gb 
			WHERE u.user_id=n.user_id 
			AND u.group_id=g.group_id 
			AND n.gubun_id=gb.gubun_id 
			ORDER BY u.user_id""")
		phoneList = self.cursor.fetchall()

		if len(phoneList) == 0:
			print("\n저장된 연락처가 없습니다.\n")
			return
		preUserId = 0;
		for row in phoneList:
			'''
				row[0] : u.user_id
				row[1] : u.user_name
				row[2] : u.group_id
				row[3] : u.e_mail
				row[4] : g.group_name
				row[5] : n.phone_num
				row[6] : gb.gubun_name
			'''
			if row[0] != preUserId:
				preUserId = row[0]
				print("\n이름 : " + row[1])
				print("이메일 : " + row[3])
				print("그룹 : " + row[4])
				print("번호 목록")

			print(row[5], row[6])

		print("")

	def showGroupPhoneList(self):
		print("\n === 4. 연락처 그룹별 보기 ===")
		self.cursor.execute(
			"""SELECT group_id, group_name FROM group_info
			ORDER BY group_id""")	
		groupList = self.cursor.fetchall()

		print("\n === 그룹 목록 ===")
		for groupItem in groupList:
			print(groupItem[0], groupItem[1])
		print("그룹 번호 입력 : ")

		groupSel = input()
		groupName = ""

		existsGroup = False

		for groupItem in groupList:
			if groupSel == groupItem[0]:
				existsGroup = True
				groupName = groupItem[1]
				break

		if not existsGroup:
			print("\n입력한 그룹 번호는 존재하지 않습니다.\n")
			return

		self.cursor.execute(
			"""SELECT u.user_id, u.user_name, u.group_id, u.e_mail, g.group_name, n.phone_num, gb.gubun_name 
			FROM user_main u, num_info n, group_info g, gubun_info gb 
			WHERE u.user_id=n.user_id 
			AND u.group_id=g.group_id 
			AND n.gubun_id=gb.gubun_id 
			AND u.group_id = :1
			ORDER BY u.user_id""", (groupSel,))

		phoneList = self.cursor.fetchall()

		if len(phoneList) == 0:
			print("\n" + groupName + " 그룹으로 저장된 번호가 없습니다.\n")
			return

		print("=== " + groupName +" 연락처 ===")
		preUserId = 0;
		for row in phoneList:
			'''
				row[0] : u.user_id
				row[1] : u.user_name
				row[2] : u.group_id
				row[3] : u.e_mail
				row[4] : g.group_name
				row[5] : n.phone_num
				row[6] : gb.gubun_name
			'''
			if row[0] != preUserId:
				preUserId = row[0]
				print("\n이름 : " + row[1])
				print("이메일 : " + row[3])
				print("그룹 : " + row[4])
				print("번호 목록")

			print(row[5], row[6])
		print("")



