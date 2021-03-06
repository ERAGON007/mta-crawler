import re

from bs4 import BeautifulSoup
from requests import get

from models import WikiFunction
from colorama import Fore, Style
from pyfiglet import figlet_format

loaded_models = []


def get_function_object(func_name):
    try:
        function_url = f"https://wiki.multitheftauto.com/wiki/{func_name}"
        page_html = get(function_url).text
        if "There is currently no text in this page" in page_html: return None
        main_soup = BeautifulSoup(page_html, "html.parser")
        function_name = str(main_soup.find("h1", attrs={'id': 'firstHeading'}).text)
        # print("Function name: ", function_name)
        mw_section = main_soup.find("div", attrs={'class': 'mw-parser-output'})
        # mw_soup = mw_section
        function_description = mw_section.find_all("p")[1].text
        # print(f"Function Description: {function_description.strip()}")
        function_syntax = str(main_soup.find_all("pre", {"class": "prettyprint lang-lua"})[0].text)
        # print("Syntax:", function_syntax)
        function_syntax = function_name + function_syntax.split(function_name)[-1]

        arguments_descriptions = {}
        arg_descriptions = mw_section.find_all("ul")[0]
        for li in arg_descriptions.find_all("li"):
            try:
                arg_text = li.text
                splitted = arg_text.split(":")
                arg_name = splitted[0].strip()
                arg_desc = splitted[1].strip()
                arguments_descriptions[arg_name] = arg_desc
            except:
                pass
        # print(arguments_descriptions)

        try:
            function_return_descriptions = main_soup.find_all("p")[2].text
            if "Note:" in function_return_descriptions:
                function_return_descriptions = main_soup.find_all("p")[3].text
            if "returns" not in function_return_descriptions.lower():
                function_return_descriptions = ""
        except:
            function_return_descriptions = ""
        # print(f"[{func_name}]Return Descriptions: ", function_return_descriptions)

        # Oh finally we're here -____-
        obj = WikiFunction(func_name=func_name, full_function_syntax=function_syntax,
                          returning=function_return_descriptions, description=function_description,
                          arg_descs=arg_descriptions)
        return obj
    except Exception as error:
        print(f"Got Error {error} [{func_name}]")
        return None


"""def get_function_object(func_name):
    page_for_function = f"https://wiki.multitheftauto.com/wiki/{func_name}"
    page_response = get(page_for_function)
    main_soup = page_response.text
    page_response_html = cleaner.clean_html(page_response.text)
    # page_response.raw.decode_content = True
    htmlparser = etree.HTMLParser()
    page_response_html = BeautifulSoup(page_response_html, "html.parser")
    tree: ElementTree = etree.parse(page_response_html)
    # func_name
    function_name = tree.find("/html/body/div[4]/h1").text
    script_side = tree.find("/html/body/div[4]/div[3]").text
    function_description = tree.find("/html/body/div[4]/div[4]/div[5]/div/p[1]").text
    function_syntax = tree.find("/html/body/div[4]/div[4]/div[5]/div/pre[1]").text
    # So the output will be dgs*() instead of float, float dgs*()
    function_syntax = function_name + function_syntax.split(function_name)[-1]

    arguments_descs = tree.find("/html/body/div[4]/div[4]/div[5]/div/ul[1]").text

    function_return_descriptions = tree.find("/html/body/div[4]/div[4]/div[5]/div/p[2]").text

    args_soup = BeautifulSoup(arguments_descs, "html.parser")

    this_function_args_descriptions = {}

    all_args: ResultSet[PageElement] = args_soup.find_all("li")
    if len(all_args) > 0:
        for li in all_args:
            splitted = str(li.text).split('"')
            arg_name = str(splitted[0].split(":")[0])
            arg_description = splitted[1].strip()
            this_function_args_descriptions[arg_name] = arg_description
    else:
        pass

    # Finally we're here -___-
    this_function_model = DgsFunction(func_name=function_name, full_function_syntax=function_syntax,
                                      side=script_side, description=function_description,
                                      returning=function_return_descriptions, arg_descs=this_function_args_descriptions)
    return this_function_model
"""


def receive_wiki_functions(url: str, script_side: str):
    class_to_import_to = ""
    ts_file = ""
    if script_side == "Client":
        class_to_import_to = "ClientDefinitions"
        ts_file = "client.ts"
    elif script_side == "Server":
        class_to_import_to = "ServerDefinitions"
        ts_file = "server.ts"
    elif script_side == "Shared":
        class_to_import_to = "SharedDefinitions"
        ts_file = "shared.ts"

    with open(ts_file, "a+") as clients_file:
        dgs_soup = BeautifulSoup(get(url).text)
        all_links = dgs_soup.find_all("a")

        for link in all_links:
            href = link.attrs.get("href")
            if href is not None:
                if "-" not in href and "On" not in href:
                    if re.match(r'/wiki/.*', href) is not None:
                        func_name = href.split("/")[-1]  # The last part is the function name
                        function_object = get_function_object(func_name=func_name)
                        if function_object is not None:
                            print(f"Got Function Object For {function_object.function_name}")
                            loaded_models.append(function_object)
                            tmp_args = ""
                            sp = function_object.full_function_name_with_args.split("(")
                            args = sp[1]
                            args = args.replace(" )", "")
                            function_object.description = function_object.description.replace('\\n', '')
                            function_object.returning_value = function_object.returning_value.replace('\\n', '')
                            args = args.split(",").__str__().replace("\\n", "")
                            function_object.function_name = function_object.function_name[
                                                                0].lower() + function_object.function_name[1:]
                            text_to_append = f"""tmpDef = new MTAFunction;
    tmpDef.label = "{function_object.function_name}";
    tmpDef.description = "{function_object.description.strip()}";
    tmpDef.returnType = "{function_object.returning_value.strip()}";
    tmpDef.args = {args};
    tmpDef.argDescs = {"{}"};
    tmpDef.scriptSide = ScriptSide.{script_side};
    {class_to_import_to}.push(tmpDef);\n\n"""
                            clients_file.writelines(text_to_append)
                            clients_file.flush()


print(Fore.CYAN, figlet_format("MTA wiki crawler"))

while True:

    print(Fore.BLUE, "========================================\n")
    print(Fore.RESET, "Options List:")

    print("1 - Generate dgs functions classes for client.ts")
    print("2 - Generate Functions List From clients.ts")
    print("3 - Generate MTA-server-functions for server.ts")
    print("4 - Generate MTA-client-functions for client.ts")
    print("5 - Generate MTA-shared-functions for shared.ts")

    operation = input("Please enter the operation number:\n")

    operation = int(operation)
    if operation == 1:
        receive_wiki_functions("https://wiki.multitheftauto.com/wiki/Resource:Dgs", "Client")
    elif operation == 2:
        with open("clients.ts", "r") as the_file:
            with open("functionsList.txt", "a+") as functions_list:
                for line in the_file.readlines():
                    if "tmpDef.label = " in line:
                        line = line.replace("tmpDef.label = ", "")
                        line = line.replace('"', "")
                        line = line.replace(';', "")
                        line = line.replace("\n", "")
                        functions_list.write(line + "|")
                        functions_list.flush()
    elif operation == 3:
        receive_wiki_functions("https://wiki.multitheftauto.com/wiki/Server_Scripting_Functions", "Server")
    elif operation == 4:
        receive_wiki_functions("https://wiki.multitheftauto.com/wiki/Client_Scripting_Functions", "Client")
    elif operation == 5:
        receive_wiki_functions("https://wiki.multitheftauto.com/wiki/Shared_Scripting_Functions", "Shared")
