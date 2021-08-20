import subprocess
import winreg
import re
import codecs

#Criando uma lista vazia onde armazenaremos todos os endereços MAC.
mac_addresses = list()

#Criando uma expressão regular (regex) para endereços MAC
macAddRegex = re.compile(r"([A-Za-z0-9]{2}[:-]){5}([A-Za-z0-9]{2})")

#Transformando dados
transportName = re.compile("({.+})")

#Criando regex para escolher o índice do adaptador de rede
adapterIndex = re.compile("([0-9]+)")

getmac_output = subprocess.run("getmac", capture_output=True).stdout.decode().split('\n')

#Loop de saida
for macAdd in getmac_output:
    #Encontrar o mac padrão
    macFind = macAddRegex.search(macAdd)

    #Encontrar o nome do transporte
    transportFind = transportName.search(macAdd)

    #Se não encontrado
    if macFind == None or transportFind == None:
        continue
    #Anexando uma tuple com o endereço Mac e o nome do transporte a uma lista
    mac_addresses.append((macFind.group(0),transportFind.group(0)))

#Menu para selecionar qual endereço Mac o usuário deseja atualizar.
print("Which MAC Address do you want to update?")
for index, item in enumerate(mac_addresses):
    print(f"{index} - Mac Address: {item[0]} - Transport Name: {item[1]}")

#Usuario deve selecionar qual deseja alterar
option = input("Select the menu item number corresponding to the MAC that you want to change:")

#Menu para que o usuário possa escolher um endereço MAC para usar
while True:
    print("Which MAC address do you want to use? This will change the Network Card's MAC address.")
    for index, item in enumerate(mac_to_change_to):
        print(f"{index} - Mac Address: {item}")

    #Escolha o Enderesso
    update_option = input("Select the menu item number corresponding to the new MAC address that you want to use:")

    #Checar se a opção escolhida é valida
    if int(update_option) >= 0 and int(update_option) < len(mac_to_change_to):
        print(f"Your Mac Address will be changed to: {mac_to_change_to[int(update_option)]}")
        break
    else:
        print("You didn't select a valid option. Please try again!")

#Caminho onde serão pesquisado valores
controller_key_part = r"SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"

#Conectando ao registro local da maquina
with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
    controller_key_folders = [("\\000" + str(item) if item < 10 else "\\00" + str(item)) for item in range(0, 21)]
    for key_folder in controller_key_folders:
        #Tentando abrir a chave para alterações
        try:
            #Conectando ao controlador key
            with winreg.OpenKey(hkey, controller_key_part + key_folder, 0, winreg.KEY_ALL_ACCESS) as regkey:
                #Avaliar se é possivel encontrar o NetCFG
                try:
                    #Iniciar contagem até que chegue em um erro no comand controller
                    count = 0
                    while True:
                        #Se encontrado valores no descompactamento, prossegue analise
                        count = count + 1

                        #Verificar se o NetCfgInstanceId é igual ao numero de transporte
                        if name == "NetCfgInstanceId" and value == mac_addresses[int(option)][1]:
                            new_mac_address = mac_to_change_to[int(update_option)]
                            winreg.SetValueEx(regkey, "NetworkAddress", 0, winreg.REG_SZ, new_mac_address)
                            print("Successly matched Transport Number")

                            #Lista de Adaptadores a desabilitar/alterar
                            break
                except WindowsError:
                    pass
        except:
            pass

#Desativar ou ativar dispositivos sem fio
run_disable_enable = input("Do you want to disable and reenable your wireless device(s). Press Y or y to continue:")

#Muda tudo para minusculo e compara com a base no While
if run_disable_enable.lower() == 'y':
    run_last_part = True
else:
    run_last_part = False

# run_last_part é definido com base na condição acima
while run_last_part:
    #Tratando lista de Adaptadores
    network_adapters = subprocess.run(["wmic", "nic", "get", "name,index"], capture_output=True).stdout.decode('utf-8', errors="ignore").split('\r\r\n')

    for adapter in network_adapters:
        #Indice de cada adaptador
        adapter_index_find = adapterIndex.search(adapter.lstrip())

        #Se houver o indice, desabilita ou habilita o adaptador
        if adapter_index_find and "Wireless" in adapter:
            disable = subprocess.run(["wmic", "path", "win32_networkadapter", "where", f"index={adapter_index_find.group(0)}", "call", "disable"],capture_output=True)

            #Se retornar 0, significa que foi desabilitado
            if(disable.returncode == 0):
                print(f"Disabled {adapter.lstrip()}")

            #Habilitar adaptador novamente
            enable = subprocess.run(["wmic", "path", f"win32_networkadapter", "where", f"index={adapter_index_find.group(0)}", "call", "enable"],capture_output=True)
            #Se retornar 0, significa que foi habilitado
            if (enable.returncode == 0):
                print(f"Enabled {adapter.lstrip()}")

    #Chamando o comando getmac novamente
    getmac_output = subprocess.run("getmac", capture_output=True).stdout.decode()

    #Recriando endereço MAC conforme formato XX-XX-XX-XX-XX-XX, com base na lista
    mac_add = "-".join([(mac_to_change_to[int(update_option)][i:i+2]) for i in range(0, len(mac_to_change_to[int(update_option)]), 2)])

    #Verificando se o MAC alterado esta no output getmac
    if mac_add in getmac_output:
        print("Mac Address Success")

    #Saida do Loop. 
    break
