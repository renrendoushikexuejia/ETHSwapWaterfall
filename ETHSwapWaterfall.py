# 2023年5月18日09:05:41 写一个ETH顺序转账的软件,输入最多6个私钥和转账金额,按照顺序从1 -> 2 -> 3 -> ... -> 6转账
# pyinstaller -w -i E:\Code\****.ico ETHSwapWaterfall.py   生成可执行文件的命令

# 保存配置文件的格式
# 

import sys,os,json,datetime
from PyQt5.QtWidgets import QMainWindow,QApplication,QMessageBox,QFileDialog,QInputDialog,QTreeWidgetItem
import pyperclip
import re
import time
from hdwallet import BIP44HDWallet
from hdwallet.utils import generate_mnemonic
# 生成私钥要导入对应的值,例如EthereumMainnet  BitcoinMainnet https://hdwallet.readthedocs.io/en/latest/cryptocurrencies.html
from hdwallet.cryptocurrencies import EthereumMainnet       
from hdwallet.cryptocurrencies import BitcoinMainnet
from hdwallet.derivations import BIP44Derivation
from web3 import Web3
from eth_account import Account
from Ui_ETHSwapWaterfallForm import Ui_ETHSwapWaterfallForm

#定义全局函数


class ETHSwapWaterfall( QMainWindow, Ui_ETHSwapWaterfallForm): 

    def __init__(self,parent =None):
        super( ETHSwapWaterfall,self).__init__(parent)
        self.setupUi(self)

        # 打开配置文件，初始化界面数据
        if os.path.exists( "./ETHSwapWaterfall.ini"):
            try:
                iniFileDir = os.getcwd() + "\\"+ "ETHSwapWaterfall.ini"
                with open( iniFileDir, 'r', encoding="utf-8") as iniFile:
                    iniDict = json.loads( iniFile.read())
                if iniDict:
                    # 这里写ETHSwapWaterfall.ini保存的初始化操作
                    pass
            except:
                QMessageBox.about( self, "提示", "打开初始化文件ETHSwapWaterfall.ini异常, 软件关闭时会自动重新创建ETHSwapWaterfall.ini文件")
        
        # 初始化交互网络选择cbNetwork
        self.cbNetwork.addItems(["Sepolia Testnet", "Goerli Testnet", "ETH Mainnet"])

        # 绑定槽函数
        self.btnHelp.clicked.connect(self.mfHelp)
        self.btnNew.clicked.connect(self.mfNew)
        self.btnOpen.clicked.connect(self.mfOpen)
        self.btnSave.clicked.connect(self.mfSave)
        self.btnGetGasPrice.clicked.connect(self.mfGetGasPrice)
        self.btnGetBalance.clicked.connect(self.mfGetAllKeyBalance)
        self.btnStart.clicked.connect(self.mfStart)

    # 使用帮助按钮  注意事项和免责声明
    def mfHelp(self):
        QMessageBox.about(self, '使用帮助', '1. ')

    # 新建文件按钮
    def mfNew(self):
        # 先保存界面上的数据
        pass
        # 先清空界面所有内容
        self.labelPath.setText("选择保存转账信息的文件.eswf")
        self.cbNetwork.setCurrentText("Sepolia Testnet")
        self.labelGasPrice.setText("---")
        self.teProjectNote.clear()
        self.leKey1.clear()
        self.leKey2.clear()
        self.leKey3.clear()
        self.leKey4.clear()
        self.leKey5.clear()
        self.leKey6.clear()
        self.labelSuccess1.clear()
        self.labelSuccess2.clear()
        self.labelSuccess3.clear()
        self.labelSuccess4.clear()
        self.labelSuccess5.clear()
        self.labelBalance1.setText("余额: *")
        self.labelBalance2.setText("余额: *")
        self.labelBalance3.setText("余额: *")
        self.labelBalance4.setText("余额: *")
        self.labelBalance5.setText("余额: *")
        self.labelBalance6.setText("余额: *")
        self.dsbAmount1.setValue(0)
        self.dsbAmount2.setValue(0)
        self.dsbAmount3.setValue(0)
        self.dsbAmount4.setValue(0)
        self.dsbAmount5.setValue(0)
        self.sbGasLimit1.setValue(21000)
        self.sbGasLimit2.setValue(21000)
        self.sbGasLimit3.setValue(21000)
        self.sbGasLimit4.setValue(21000)
        self.sbGasLimit5.setValue(21000)
        self.sbGasPrice1.setValue(0)
        self.sbGasPrice2.setValue(0)
        self.sbGasPrice3.setValue(0)
        self.sbGasPrice4.setValue(0)
        self.sbGasPrice5.setValue(0)
        self.teLog.clear()

        try:
            desktopPath = os.path.join(os.path.expanduser("~"), "Desktop")
            tempFolderPath = QFileDialog.getExistingDirectory( self, '选择保存目录', desktopPath, QFileDialog.ShowDirsOnly)
            tempFileName, ok = QInputDialog.getText(self, '新建文件', '请输入新建文件名称:') 
            if ok and tempFolderPath and tempFileName and tempFolderPath != None:
                filePath = tempFolderPath + '/' + tempFileName + '.eswf'
                if os.path.exists(filePath):
                    QMessageBox.about( self, '提示', '文件名称重复,为了保证数据安全,本软件禁止保存重名文件')
                    return
                f = open( filePath, 'x')
                # 初始化文件中的内容, 这里不需要写入内容,只需要写入一个空字典
                tempDict = {}
                tempJson = json.dumps(tempDict, indent=4)
                f.write(tempJson)
                f.close()
            else:
                QMessageBox.about( self, '提示', '文件名或路径错误')
                return

            self.labelPath.setText(filePath)

        except:
            QMessageBox.about( self, '提示', '文件创建失败')
            return
        

    # 打开文件按钮, 点击按钮打开文件对话框,获得文件路径,传递给mfRefresh()刷新界面
    def mfOpen(self):
        desktopPath = os.path.join(os.path.expanduser("~"), "Desktop")
        # try:
        tempFilePath, uselessFilt = QFileDialog.getOpenFileName( self, '打开文件', desktopPath, '转账文件(*.eswf)', '转账文件(*.eswf)')
        if tempFilePath != '':
            self.labelPath.setText(tempFilePath)
            # 读取eswf文件内容,并更新界面
            with open( tempFilePath, 'r', encoding="utf-8") as tempFile:
                tempDict = json.loads( tempFile.read())
            if tempDict:
                self.teProjectNote.setHtml(tempDict['projectNote'])
                self.cbNetwork.setCurrentText(tempDict['network'])

                self.leKey1.setText(tempDict['key1'])
                self.dsbAmount1.setValue(tempDict['amount1'])
                self.sbGasLimit1.setValue(tempDict['gasLimit1'])
                self.sbGasPrice1.setValue(tempDict['gasPrice1'])

                self.leKey2.setText(tempDict['key2'])
                self.dsbAmount2.setValue(tempDict['amount2'])
                self.sbGasLimit2.setValue(tempDict['gasLimit2'])
                self.sbGasPrice2.setValue(tempDict['gasPrice2'])

                self.leKey3.setText(tempDict['key3'])
                self.dsbAmount3.setValue(tempDict['amount3'])
                self.sbGasLimit3.setValue(tempDict['gasLimit3'])
                self.sbGasPrice3.setValue(tempDict['gasPrice3'])

                self.leKey4.setText(tempDict['key4'])
                self.dsbAmount4.setValue(tempDict['amount4'])
                self.sbGasLimit4.setValue(tempDict['gasLimit4'])
                self.sbGasPrice4.setValue(tempDict['gasPrice4'])

                self.leKey5.setText(tempDict['key5'])
                self.dsbAmount5.setValue(tempDict['amount5'])
                self.sbGasLimit5.setValue(tempDict['gasLimit5'])
                self.sbGasPrice5.setValue(tempDict['gasPrice5'])

                self.leKey6.setText(tempDict['key6'])
            
        else:
            QMessageBox.about( self, "提示", "请选择后缀名为 .eswf 的文件。")
        # except:
        #     QMessageBox.about( self, "提示", "选择keyManager文件失败,请重新选择。")

    # 保存按钮,点击保存,把界面数据转换为json格式,保存在当前打开的文件self.labelPath.text()中
    def mfSave(self):
        saveFilePath = self.labelPath.text()
        if saveFilePath[0] == '选':      # 如果保存的文件名是 '选择保存转账信息的文件.eswf'
            try:
                desktopPath = os.path.join(os.path.expanduser("~"), "Desktop")
                tempFolderPath = QFileDialog.getExistingDirectory( self, '选择保存目录', desktopPath, QFileDialog.ShowDirsOnly)
                tempFileName, ok = QInputDialog.getText(self, '新建文件', '请输入新建文件名称:') 
                if ok and tempFolderPath and tempFileName and tempFolderPath != None:
                    filePath = tempFolderPath + '/' + tempFileName + '.eswf'
                    if os.path.exists(filePath):
                        QMessageBox.about( self, '提示', '文件名称重复,为了保证数据安全,本软件禁止保存重名文件')
                        return
                    f = open( filePath, 'x')
                    # 初始化文件中的内容, 这里不需要写入内容,只需要写入一个空字典
                    tempDict = {}
                    tempJson = json.dumps(tempDict, indent=4)
                    f.write(tempJson)
                    f.close()
                else:
                    QMessageBox.about( self, '提示', '文件名或路径错误')
                    return
            except:
                QMessageBox.about( self, '提示', '文件创建失败')
                return
            
            saveFilePath = filePath
            self.labelPath.setText(saveFilePath)

        # print(saveFilePath)
        # 获得界面上的数据 存入字典
        tempDict = {'projectPath': saveFilePath, 'projectCreationTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'projectNote': self.teProjectNote.toHtml(), 'network': self.cbNetwork.currentText(), 
        'key1': self.leKey1.text(), 'amount1': self.dsbAmount1.value(), 'gasLimit1': self.sbGasLimit1.value(), 'gasPrice1': self.sbGasPrice1.value(),
        'key2': self.leKey2.text(), 'amount2': self.dsbAmount2.value(), 'gasLimit2': self.sbGasLimit2.value(), 'gasPrice2': self.sbGasPrice2.value(),
        'key3': self.leKey3.text(), 'amount3': self.dsbAmount3.value(), 'gasLimit3': self.sbGasLimit3.value(), 'gasPrice3': self.sbGasPrice3.value(),
        'key4': self.leKey4.text(), 'amount4': self.dsbAmount4.value(), 'gasLimit4': self.sbGasLimit4.value(), 'gasPrice4': self.sbGasPrice4.value(),
        'key5': self.leKey5.text(), 'amount5': self.dsbAmount5.value(), 'gasLimit5': self.sbGasLimit5.value(), 'gasPrice5': self.sbGasPrice5.value(),
        'key6': self.leKey6.text()}

        saveJson = json.dumps( tempDict, indent=4)
        try:
            saveFile = open( saveFilePath, "w",  encoding="utf-8")
            saveFile.write( saveJson)
            saveFile.close()
        except:
            QMessageBox.about( self, "提示", "保存转账数据文件.eswf失败")

    # 检查字符串是否符合ETH私钥规则
    def is_valid_ethereum_private_key(self, key: str) -> bool:
        # 检查字符串是否为十六进制
        if not re.fullmatch(r'^[0-9a-fA-F]+$', key):
            return False

        # 检查字符串长度是否为 64
        if len(key) != 64:
            return False

        return True

    # 根据下拉列表框cbNetwork的内容  获得对应的Web3.HTTPProvider
    def mfGetWeb3HTTPProvider(self):
        network = self.cbNetwork.currentText()
        # ["Sepolia Testnet", "Goerli Testnet", "ETH Mainnet"]
        if network == 'Sepolia Testnet':
            w3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/7c1b8b9a7f4c431ab978bcb373a9fd32'))       # sepolia测试网
        elif network == 'Goerli Testnet':
            w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/7c1b8b9a7f4c431ab978bcb373a9fd32'))    # goerli 测试网
        elif network == 'ETH Mainnet':
            w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/7c1b8b9a7f4c431ab978bcb373a9fd32'))   # ETH 主网

        return w3


    # 获得当前gas price 并更新界面
    def mfGetGasPrice(self):
        self.labelGasPrice.setText("查询中")
        w3 = self.mfGetWeb3HTTPProvider()
        gasPrice = w3.from_wei(w3.eth.gas_price, 'gwei')
        self.labelGasPrice.setText(str(gasPrice))

    #  已知私钥,查询余额
    def mfGetBalance(self, key):
        w3 = self.mfGetWeb3HTTPProvider()
        address = Account.from_key(key).address
        balanceWei = w3.eth.get_balance(address)
        balanceETH = round(w3.from_wei(balanceWei, 'ether'), 4)
        return balanceETH

    # 点击余额查询,查询所有输入的私钥余额,并更新界面
    def mfGetAllKeyBalance(self):
        # print(self.mfGetBalance('3f89d36b13d07d01bb3192ab7c801dbc702da59b195832e18f871ec5'))
        if self.leKey1.text():
            if self.is_valid_ethereum_private_key(self.leKey1.text()):
                self.labelBalance1.setText("余额: " + str(self.mfGetBalance(self.leKey1.text())))
            
        if self.leKey2.text():
            if self.is_valid_ethereum_private_key(self.leKey2.text()):
                self.labelBalance2.setText("余额: " + str(self.mfGetBalance(self.leKey2.text())))

        if self.leKey3.text():
            if self.is_valid_ethereum_private_key(self.leKey3.text()):
                self.labelBalance3.setText("余额: " + str(self.mfGetBalance(self.leKey3.text())))
        
        if self.leKey4.text():
            if self.is_valid_ethereum_private_key(self.leKey4.text()):
                self.labelBalance4.setText("余额: " + str(self.mfGetBalance(self.leKey4.text())))
            
        if self.leKey5.text():
            if self.is_valid_ethereum_private_key(self.leKey5.text()):
                self.labelBalance5.setText("余额: " + str(self.mfGetBalance(self.leKey5.text())))

        if self.leKey6.text():
            if self.is_valid_ethereum_private_key(self.leKey6.text()):
                self.labelBalance6.setText("余额: " + str(self.mfGetBalance(self.leKey6.text())))

    # 转账函数,参数为 发送方私钥, 接收方私钥, 转账金额, gas price, gas limit
    def transfer_eth(self, sender_private_key: str, receiver_private_key: str, chainID: int,eth_amount: float, 
                 gas_price: int, gas_limit: int) -> tuple[bool, str]:
        w3 = self.mfGetWeb3HTTPProvider()
        # 获取发送方和接收方地址
        sender_address = Account.from_key(sender_private_key).address
        receiver_address = Account.from_key(receiver_private_key).address


        # tempBalance = w3.eth.get_balance(sender_address)
        # tempBalance = w3.from_wei( tempBalance, 'ether')
        # print(tempBalance)
        # print('gas_price', type(gas_price))
        # print('w3.eth.gas_price', w3.eth.gas_price)
        # 计算交易所需的gas
        if not gas_price:   # 判断gas_price为0或空
            gas_price = w3.eth.gas_price
        if not gas_limit:
            gas_limit = 21000       # 发送以太币所需的标准gas数量

        value = w3.to_wei(eth_amount, 'ether')
        transaction_cost = gas_price * gas_limit + value
        
        # 检查发送方余额是否充足
        sender_balance = w3.eth.get_balance(sender_address)
        if sender_balance < transaction_cost:
            return False, '余额不足'
        
        # 构造交易
        nonce = w3.eth.get_transaction_count(sender_address)       
        transaction = {
            'from': sender_address,
            'to': receiver_address,
            'value': value,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': chainID     # 区块链网络的ID
        }
        
        # print(transaction)
        # 签名交易并发送
        signed_transaction = w3.eth.account.sign_transaction(transaction, sender_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        
        # 等待交易完成
        w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return True, '交易成功'


    # 点击开始转账btnStart
    def mfStart(self):
        self.labelSuccess1.clear()
        self.labelSuccess2.clear()
        self.labelSuccess3.clear()
        self.labelSuccess4.clear()
        self.labelSuccess5.clear()

        QApplication.processEvents()        # 这一行很重要,在执行耗时操作之前调用,可以刷新界面

        key1 = self.leKey1.text()
        key2 = self.leKey2.text()
        key3 = self.leKey3.text()
        key4 = self.leKey4.text()
        key5 = self.leKey5.text()
        key6 = self.leKey6.text()

        network = self.cbNetwork.currentText()
        if network == 'Sepolia Testnet':
            chainID = 11155111
        elif network == 'Goerli Testnet':
            chainID = 5
        elif network == 'ETH Mainnet':
            chainID = 1


        if key1 and key2:
            self.labelSuccess1.setText("🗲 转账中 " + str(self.dsbAmount1.value()) + " 🗲")
            QApplication.processEvents()
            resultBool, resultStr = self.transfer_eth(key1, key2, chainID, self.dsbAmount1.value(), 
                                                      self.sbGasPrice1.value(), self.sbGasLimit1.value())
            if not resultBool:
                self.labelSuccess1.setText("✖ 转账出错 " + str(self.dsbAmount1.value()) + " ✖")
                QMessageBox.about(self, "提示", "key1转账到key2出现错误 " + resultStr)
                return
            self.labelSuccess1.setText("🡻 转账成功 " + str(self.dsbAmount1.value()) + " 🡻")

        if key2 and key3:
            self.labelSuccess2.setText("🗲 转账中 " + str(self.dsbAmount2.value()) + " 🗲")
            QApplication.processEvents()
            resultBool, resultStr = self.transfer_eth(key2, key3, chainID, self.dsbAmount2.value(), 
                                                      self.sbGasPrice2.value(), self.sbGasLimit2.value())
            if not resultBool:
                self.labelSuccess2.setText("✖ 转账出错 " + str(self.dsbAmount2.value()) + " ✖")
                QMessageBox.about(self, "提示", "key2转账到key3出现错误 " + resultStr)
                return
            self.labelSuccess2.setText("🡻 转账成功 " + str(self.dsbAmount2.value()) + " 🡻")

        if key3 and key4:
            self.labelSuccess3.setText("🗲 转账中 " + str(self.dsbAmount3.value()) + " 🗲")
            QApplication.processEvents()
            resultBool, resultStr = self.transfer_eth(key3, key4, chainID, self.dsbAmount3.value(), 
                                                      self.sbGasPrice3.value(), self.sbGasLimit3.value())
            if not resultBool:
                self.labelSuccess3.setText("✖ 转账出错 " + str(self.dsbAmount3.value()) + " ✖")
                QMessageBox.about(self, "提示", "key3转账到key4出现错误 " + resultStr)
                return
            self.labelSuccess3.setText("🡻 转账成功 " + str(self.dsbAmount3.value()) + " 🡻")

        if key4 and key5:
            self.labelSuccess4.setText("🗲 转账中 " + str(self.dsbAmount4.value()) + " 🗲")
            QApplication.processEvents()
            resultBool, resultStr = self.transfer_eth(key4, key5, chainID, self.dsbAmount4.value(), 
                                                      self.sbGasPrice4.value(), self.sbGasLimit4.value())
            if not resultBool:
                self.labelSuccess4.setText("✖ 转账出错 " + str(self.dsbAmount4.value()) + " ✖")
                QMessageBox.about(self, "提示", "key4转账到key5出现错误 " + resultStr)
                return
            self.labelSuccess4.setText("🡻 转账成功 " + str(self.dsbAmount4.value()) + " 🡻")

        if key5 and key6:
            self.labelSuccess5.setText("🗲 转账中 " + str(self.dsbAmount5.value()) + " 🗲")
            QApplication.processEvents()
            resultBool, resultStr = self.transfer_eth(key5, key6, chainID, self.dsbAmount5.value(), 
                                                      self.sbGasPrice5.value(), self.sbGasLimit5.value())
            if not resultBool:
                self.labelSuccess5.setText("✖ 转账出错 " + str(self.dsbAmount5.value()) + " ✖")
                QMessageBox.about(self, "提示", "key5转账到key6出现错误 " + resultStr)
                return
            self.labelSuccess5.setText("🡻 转账成功 " + str(self.dsbAmount5.value()) + " 🡻")

        self.mfGetAllKeyBalance()       # 更新显示所有余额


        
#主程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = ETHSwapWaterfall()
    myWin.show()

    appExit = app.exec_()
    #退出程序之前，保存界面上的设置
    myWin.mfSave()      # 保存打开的km文件

    sys.exit( appExit)
