import cx_Oracle as cxo
import phone_book as pb

if __name__ == "__main__":
	# DB연결 정보 수정
	dbID = "oracle"
	dbPwd = "tiger"
	#dbIP = "localhost"
	dbIP = "172.30.1.49"
	dbPort = 1521
	dbName = "orcl"

	pbi = pb.phoneBook()
	pbi.connectOracle(dbID, dbPwd, dbIP, dbPort, dbName)

	while True:
		menuNum = pbi.selectMenu()

		if menuNum == "1":
			pbi.insertNewPhone()
		elif menuNum == "2":
			pbi.searchPhone()
		elif menuNum == "3":
			pbi.showAllPhoneList()
		elif menuNum == "4":
			pbi.showGroupPhoneList()
		elif menuNum == "0":
			print("\n프로그램을 종료합니다.")
			pbi.closeOracle()
			break
		else:
			print("메뉴에 제시된 번호만을 입력해주세요\n")