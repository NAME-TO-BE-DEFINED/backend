import web3
import os
from dotenv import load_dotenv
import json
from pprint import pprint

load_dotenv()

class CTF:
    def __init__(self, Infura_endpoint, SWAP_ADDRESS, SWAP_provider, BALANCER_POOL_ADDRESS, BALANCER_QUERIES, ChainId, usdcAddress):
        
        Infura_key = os.getenv("infura_key")
        self.w3 = web3.Web3(web3.HTTPProvider(Infura_endpoint))
        self.c3 = web3.Web3(web3.HTTPProvider(f"https://optimism-sepolia.infura.io/v3/{Infura_key}"))
        self.CTF_ADDRESS = "0xBb77B4F79AD58165aA6F3da97fc67c5178BbC0C5"
        self.PoolManager = "0xa38Ead530857Cfc218a76807d2732128745e6c03"
        self.SWAP_provider = SWAP_provider
        self.ChainId = ChainId
        self.Tokenprice = 0.5
        self.usdcAddress = usdcAddress

        with open("ABI/swap_abi.json") as file:
            SWAP_ABI = json.load(file)

        with open("ABI/ctf_abi.json") as file:
            CTF_ABI = json.load(file)

        with open("ABI/balancer_pool.json") as file:
            BALANCER_POOL_ABI = json.load(file)

        with open("ABI/balancer_quries.json") as file:
            BALANCER_QUERIES_ABI = json.load(file)

        with open("ABI/PoolManager.json") as file:
            POOL_MANAGER_ABI = json.load(file)

        self.ctf_contract = self.c3.eth.contract(address=self.CTF_ADDRESS, abi=CTF_ABI)
        self.swap_contract = self.w3.eth.contract(address=SWAP_ADDRESS, abi=SWAP_ABI)
        self.balancer_pool_contract = self.w3.eth.contract(address=BALANCER_POOL_ADDRESS, abi=BALANCER_POOL_ABI)
        self.balancer_quries_contract = self.w3.eth.contract(address=BALANCER_QUERIES, abi=BALANCER_QUERIES_ABI)
        self.pool_manager_contract = self.w3.eth.contract(address=self.PoolManager, abi=POOL_MANAGER_ABI)

    #def swap_calldata(self):
        


    def withraw(self, CTF_amount):
        
        PoolId = self.getPoolId()
        ExitTokenIndex = self.getExitTokenIndex(PoolId)
        CTF_amount = self.getCtfAmountChain(CTF_amount)
        ExitPoolData = self.getExitPoolData(PoolId, ExitTokenIndex[0], CTF_amount)
        BalancerData = self.getBalancerQuries(PoolId, ExitPoolData)

        bptIn = BalancerData[0]
        ammountsOut = BalancerData[1]
        ammountsOut = max(ammountsOut)
        usdcValue = int(ammountsOut * self.Tokenprice)
        

        swapCalldata = self.swap_contract.encode_abi(fn_name="swapToUSDC", args=[self.CTF_ADDRESS, ammountsOut, self.usdcAddress, usdcValue]) # math scary

        ExitTokenAmount = ExitTokenIndex[1][ExitTokenIndex[0]]
        onepercent = ExitTokenAmount * 0.99
        onepercent = int(onepercent)

        data = {
            "bptAmountPerChain": CTF_amount,
            "swapProvider": self.SWAP_provider,
            "ExitTokenIndex": ExitTokenIndex[0],
            "SwapsCalldata": swapCalldata,
            "exitTokenMinAmountOut": onepercent
        }
        

        return data


    def deposit(self, usdcAmount):
        # too lazy to create another function
        usdcAmountPerChain = usdcAmount / len(self.ctf_contract.functions.getChains().call())


        poolId = self.getPoolId()
        ExitTokendata = self.getExitTokenIndex(poolId)
        
        usdcAmountPerToken = int(usdcAmountPerChain / len(ExitTokendata[3]))
        TokenAmount = usdcAmountPerToken * 2

        def defcalldata(TokenAddress):
            calldata = self.swap_contract.encode_abi(fn_name="swapFromUSDC", args=[self.usdcAddress, TokenAddress, int(usdcAmountPerToken), int(TokenAmount)])
            return calldata

        swapCalldata = []


        for i in ExitTokendata[3]:
            swapCalldata.append(defcalldata(i))



        data = {
            "minBPTOut": 1,
            "SwapsProvider": self.SWAP_provider,
            "usdcAmount": usdcAmountPerChain,
            "swapcalldata": swapCalldata
        }
        

        return data
        





    

    def getPoolId(self):
        ChainPoolData = self.ctf_contract.functions.getChainPool(self.ChainId).call()
        PoolId = ChainPoolData[3]
        return PoolId


    def getExitTokenIndex(self, PoolId):
        r = self.balancer_pool_contract.functions.getPoolTokens(PoolId).call()
        r[0].pop(0) # remove bpt token 
        r[1].pop(0)
        HighestSupply = max(r[1][1:])
        ExitTokenIndex = r[1].index(HighestSupply)
        return [ExitTokenIndex, r[1], r[0][ExitTokenIndex], r[0]]

    
    def getCtfAmountChain(self, CTF_amount):
        CTF_chains = self.ctf_contract.functions.getChains().call()
        CTF_per_chain = CTF_amount / len(CTF_chains)
        return int(CTF_per_chain)

    
    def getExitPoolData(self, PoolId, ExitTokenIndex, CTF_amount):
        if self.ChainId == 84532: # hardcoding bad but me have no choice time late
            ExitPoolData = self.pool_manager_contract.functions.getExitPoolData(PoolId, ExitTokenIndex, CTF_amount, 0).call()
        else:
            ExitPoolData = self.ctf_contract.functions.getExitPoolData(PoolId, ExitTokenIndex, CTF_amount, 0).call()

        ExitPoolData.pop()
        ExitPoolData = ExitPoolData[0]
        return ExitPoolData

    def getBalancerQuries(self, PoolId, ExitPoolData):
        e = self.balancer_quries_contract.functions.queryExit(PoolId, self.CTF_ADDRESS, self.CTF_ADDRESS, ExitPoolData).call()
        return e

    


# ctf.withraw(100)
# Infura_key = os.getenv("infura_key")
# chains = {
#     "optimism": {
#         "ENDPOINT": f"https://optimism-sepolia.infura.io/v3/{Infura_key}",
#         "SWAP_ADDRESS": "0xdc478014d9c22969A82CD6dfb2Fa441618f3462b",
#         "SWAP_provider": "0xdc478014d9c22969A82CD6dfb2Fa441618f3462b",
#         "BALANCER_POOL_ADDRESS": "0x75DFc9064614498EDD9FAd00857d4917CAaDdeE5",
#         "BALANCER_QUERIES": "0x268eb558B65526361599aB4108d3Ef53c3dB97b5",
#         "ChainId": 11155420,
#         "usdcAddress": "0x5fd84259d66Cd46123540766Be93DFE6D43130D7"
#     },
#     "base": {
#         "ENDPOINT": f"https://base-sepolia.infura.io/v3/{Infura_key}",
#         "SWAP_ADDRESS": "0xF4b37DBA9D8382294e66882dcfD55d65dDbAbFd2",
#         "SWAP_provider": "0xF4b37DBA9D8382294e66882dcfD55d65dDbAbFd2",
#         "BALANCER_POOL_ADDRESS": "0x5cc729e3099e6372E0e9406613E043e609d789be",
#         "BALANCER_QUERIES": "0xaFEE0F279375E9544C4a745340487f4Cd9B5D17a",
#         "ChainId": 84532,
#         "usdcAddress": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
#     }
# }



# data = {}
# amount = 10e6
# for key, value in chains.items():
#     ctf = CTF(Infura_endpoint=value["ENDPOINT"], SWAP_ADDRESS=value["SWAP_ADDRESS"], SWAP_provider=value["SWAP_provider"], BALANCER_POOL_ADDRESS=value["BALANCER_POOL_ADDRESS"], BALANCER_QUERIES=value["BALANCER_QUERIES"], ChainId=value["ChainId"], usdcAddress=value["usdcAddress"])
#     e = ctf.withraw(amount)
#     print("DONE!")
#     data[key] = e


# for key, value in chains.items():
#     ctf = CTF(Infura_endpoint=value["ENDPOINT"], SWAP_ADDRESS=value["SWAP_ADDRESS"], SWAP_provider=value["SWAP_provider"], BALANCER_POOL_ADDRESS=value["BALANCER_POOL_ADDRESS"], BALANCER_QUERIES=value["BALANCER_QUERIES"], ChainId=value["ChainId"], usdcAddress=value["usdcAddress"])
#     e = ctf.deposit(amount)
#     print("DONE!")
#     data[key] = e


