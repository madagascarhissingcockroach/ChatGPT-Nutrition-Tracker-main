from tkinter import *
from typing import Any
import customtkinter as ctk
from PIL import Image
import gpt
from functools import partial
import json
from datetime import date

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("Anthracite.json")

sasFoods = [
    "Hainanese chicken rice",
    "Pad thai",
    "Butter chicken rice/naan",
    "Beef/Chicken burrito",
    "Chicken nuggets",
    "French fries",
    "Blueberry muffin",
    "Banana muffin",
    "Gluten-free muffin",
    "Chicken pie",
    "Frozen yoghurt",
    "Tuna mayo sandwich (white bread)",
    "Chicken sandwich (white bread)",
    "Chicken/beef meatball pasta",
    "Chicken/beef quesadilla"
]

class Food:
    name=""
    calories=0
    sugar=0
    protein=0
    fat=0
    carbs=0
    fiber=0
    
    def __init__(self, name, calories, sugar, protein, fat, carbs, fiber) -> None:
        self.name=name
        self.calories=calories
        self.sugar=sugar
        self.protein=protein
        self.fat=fat
        self.carbs=carbs
        self.fiber=fiber

class User:
    name = ""
    foodsArr = []
    componentGoals = {
        "calories": 0,
        "sugar": 0,
        "protein": 0,
        "fat": 0,
        "carbs": 0,
        "fiber": 0
    }
    per2000Goals = {
        "calories": 2000,
        "sugar": 40,
        "protein": 75,
        "fat": 60,
        "carbs": 300,
        "fiber": 28
    }

    def addFood(self, food):
        self.foodsArr.append(food)
    
    def setCalorieGoal(self, calorieGoal):
        self.componentGoals["calories"] = calorieGoal
        calorieRatio = self.componentGoals["calories"]/self.per2000Goals["calories"]
        self.componentGoals["sugar"] = round(calorieRatio * self.per2000Goals["sugar"], 1)
        self.componentGoals["protein"] = round(calorieRatio * self.per2000Goals["protein"], 1)
        self.componentGoals["fat"] = round(calorieRatio * self.per2000Goals["fat"], 1)
        self.componentGoals["carbs"] = round(calorieRatio * self.per2000Goals["carbs"], 1)
        self.componentGoals["fiber"] = round(calorieRatio * self.per2000Goals["fiber"], 1)

        with open('userInfo.json') as infoJson:
            storedUserInfo = json.load(infoJson)
            storedUserInfo["maintenanceCalories"] = calorieGoal
            jsonObject = json.dumps(storedUserInfo)
            with open("userInfo.json", "w") as writeInfoJson:
                writeInfoJson.write(jsonObject)
    
    def count(self, attribute):
        sum = 0
        for food in self.foodsArr:
            sum += getattr(food, attribute, "None")
        return round(sum, 2)

    def findHighest(self, attribute):
        highestNumber = 0
        highestFood = None
        for food in self.foodsArr:
            currentAttr = getattr(food, attribute, 0)
            if currentAttr > highestNumber:
                highestNumber = currentAttr
                highestFood = food
        return highestFood

    def getNutrition(self) -> dict:
        nutrition = {}
        for attribute in self.componentGoals:
            nutrition[attribute] = self.count(attribute)
        return nutrition

    def getSerializableArr(self):
        attributes = ["name", "calories", "sugar", "protein", "fat", "carbs", "fiber"]
        serializableArr = []
        for food in self.foodsArr:
            foodDict = {}
            for attribute in attributes:
                foodDict[attribute] = getattr(food, attribute)
            serializableArr.append(foodDict)
        return serializableArr

def menu():
    displayMenu()

def exit():
    save(False)
    root.quit()

def displayTitle():
    global titleFrame
    if "menuFrame" in globals():
        menuFrame.destroy()
    titleFrame = ctk.CTkFrame(master = root, corner_radius=25)
    titleFrame.place(relx=0.5, rely=0.5, anchor="center")

    title = ctk.CTkLabel(master = titleFrame, text = "Nutrition Tracker", font = (globalFontFamily, 60))
    title.pack(pady = (60, 30), padx=75)

    startButton = ctk.CTkButton(master = titleFrame, command=menu, height=100, width=400, text="Start", font=(globalFontFamily, 50), corner_radius=25)
    startButton.pack(pady=30, padx=50)

    cross = ctk.CTkImage(light_image=Image.open("assets/cross.png"), size=(30, 30))
    exitButton = ctk.CTkButton(master=titleFrame, command=exit, height=100, width=400, text="Exit", font=(globalFontFamily, 50), image=cross, corner_radius=25)
    exitButton.pack(pady=(30, 60), padx=50)

def startProgram():
    # create the user
    global user
    user = User()

    # create the window
    global root
    root = ctk.CTk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    root.title("Nutrition Tracker")

    # create the bg
    background=ctk.CTkImage(light_image=Image.open("assets/bg.jpeg"), size=(2000, 1000))
    bgLabel=ctk.CTkLabel(master=root, image=background, text="")
    bgLabel.place(relx=0, rely=0)

    # writes the most recent info from userHistory.json to user class if its found and isn't done
    with open('userHistory.json') as history:
        history = json.load(history)
        if len(history) > 0:
            recentLog = history[len(history)-1]

            # converts arr of dicts back into arr of Foods
            if recentLog["done"] == False:
                for foodDict in recentLog["foodsArr"]:
                    user.addFood(Food(foodDict["name"], foodDict["calories"], foodDict["sugar"], foodDict["protein"], foodDict["fat"], foodDict["carbs"], foodDict["fiber"]))

    with open('userInfo.json') as infoJson:
        storedUserInfo = json.load(infoJson)
        user.setCalorieGoal(storedUserInfo["maintenanceCalories"])
    
    global globalFontFamily
    globalFontFamily = "Times"

    global visibleFrames 
    visibleFrames = []

    displayTitle()

startProgram()

def displayMenu():
    global menuFrame

    if "titleFrame" in globals():
        titleFrame.destroy()
    if "enterFrame" in globals():
        enterFrame.destroy()
    if "logFrame" in globals():
        logFrame.destroy()
    if "analysisFrame" in globals():
        analysisFrame.destroy()
    if user.componentGoals["calories"] == 0:
        calorieGoalPrompt()
        return

    global visibleFrames
    visibleFrames = []

    menuFrame = ctk.CTkFrame(master=root, corner_radius=25)
    menuFrame.place(rely=0.5, relx=0.5, anchor="center")

    menuLabel = ctk.CTkLabel(master=menuFrame, text="Menu", font=(globalFontFamily, 50))
    menuLabel.grid(column=2, row=0, pady=30)

    enterButton = ctk.CTkButton(master=menuFrame, height=75, width=400, text="Add a food", font=(globalFontFamily, 30), command=displayEnter, corner_radius=25)
    enterButton.grid(column=1, row=2, padx=30, pady=50)

    enterIcon = ctk.CTkImage(light_image=Image.open("assets/enter.png"), size=(250, 250))
    enterLabel = ctk.CTkLabel(master=menuFrame, text="", image=enterIcon)
    enterLabel.grid(column=1, row=1, padx=30, pady=30)

    logButton = ctk.CTkButton(master=menuFrame, height=75, width=400, text="View log", font=(globalFontFamily, 30), command=displayLog, corner_radius=25)
    logButton.grid(column=2, row=2, padx=30, pady=50)

    logIcon = ctk.CTkImage(light_image=Image.open("assets/log.png"), size=(250, 250))
    logLabel = ctk.CTkLabel(master=menuFrame, text="", image=logIcon)
    logLabel.grid(column=2, row=1, padx=30, pady=30)

    analysisButton = ctk.CTkButton(master=menuFrame, height=75, width=400, text="Analyze", font=(globalFontFamily, 30), command=displayAnalysis, corner_radius=25)
    analysisButton.grid(column=3, row=2, padx=30, pady=50)

    analysisIcon = ctk.CTkImage(light_image=Image.open("assets/analyze.png"), size=(250, 250))
    analysisLabel = ctk.CTkLabel(master=menuFrame, text="", image=analysisIcon)
    analysisLabel.grid(column=3, row=1, padx=30, pady=30)

    global menuBackButton
    backIcon = ctk.CTkImage(light_image=Image.open("assets/back.png"), size=(30, 30))
    menuBackButton = ctk.CTkButton(master=menuFrame, image=backIcon, text="Back", width=40, height=40, command=displayTitle)
    menuBackButton.place(relx = 0.03, rely = 0.08)

def calorieGoalPrompt():
    global goalFrame
    goalFrame = ctk.CTkFrame(master=root, corner_radius=25)
    goalFrame.place(relx=0.5, rely=0.5, anchor="center")

    goalQuestion = ctk.CTkLabel(master=goalFrame, text="What are your daily maintenance calories?", font=(globalFontFamily, 50))
    goalQuestion.pack(padx=100, pady=(100, 50))

    global goalEntry
    goalEntry = ctk.CTkEntry(master=goalFrame, width=300, height=100, font=(globalFontFamily, 45), justify="center", corner_radius=25)
    goalEntry.pack(padx=50, pady=50)

    goalEnter = ctk.CTkButton(master=goalFrame, width=400, height=100, corner_radius=25, command=goalEnd, text="Enter", font=(globalFontFamily, 50))
    goalEnter.pack(padx=50, pady=(50, 100))

def goalEnd():
    try:
        int(goalEntry.get())
    except:
        pass
    else:
        user.setCalorieGoal(int(goalEntry.get()))
        goalFrame.destroy()
        displayMenu()

def displayAnalysis():
    global analysisFrame # column number = 3
    analysisFrame = ctk.CTkFrame(master=root, corner_radius=25, width=5000)
    
    menuFrame.destroy()

    analysisLabel = ctk.CTkLabel(master=analysisFrame, text="Analysis", font=(globalFontFamily, 50))
    analysisLabel.grid(column = 1, row = 1, columnspan = 3, padx=500, pady=50)

    currentButton = ctk.CTkButton(master=analysisFrame, text="Current Log", width=200, height=40, font=(globalFontFamily, 30), command=analysisCurrent, corner_radius=25)
    currentButton.grid(column=1, row=2, padx=50)

    historyButton = ctk.CTkButton(master=analysisFrame, text="Past Logs", width=200, height=40, font=(globalFontFamily, 30), command=analysisHistory, corner_radius=25)
    historyButton.grid(column=2, row=2, padx=50)

    suggestionsButton = ctk.CTkButton(master=analysisFrame, text="Suggestions", width=200, height=40, font=(globalFontFamily, 30), command=analysisSuggestions, corner_radius=25)
    suggestionsButton.grid(column=3, row=2, padx=50)

    backIcon = ctk.CTkImage(light_image=Image.open("assets/back.png"), size=(30, 30))
    analysisBackButton = ctk.CTkButton(master=analysisFrame, image=backIcon, text="Back", width=30, height=30, command=displayMenu, font=(globalFontFamily, 20), corner_radius=25)
    analysisBackButton.place(relx = 0.03, rely = 0.08)

    global gptSuggestion
    gptSuggestion = getSuggestionGPT()

    analysisCurrent()
    analysisFrame.place(relx=0.5, rely=0.5, anchor="center")

def analysisCurrent():
    global analysisCurrentFrame
    if "analysisCurrentFrame" in globals() and analysisCurrentFrame in visibleFrames:
        return
    
    print(gptSuggestion)
    analysisCurrentFrame = ctk.CTkScrollableFrame(master=analysisFrame, corner_radius=25, width=1000, height=498)
    visibleFrames.append(analysisCurrentFrame)

    for macro in ["calories", "sugar", "protein", "fat", "carbs", "fiber"]:
        label = ctk.CTkLabel(master=analysisCurrentFrame, text=analyzeMacroText(macro) + "\n" + gptSuggestion[macro], font=(globalFontFamily, 30), wraplength=900)
        label.grid(padx=50, pady=25)

    renewLogButton = ctk.CTkButton(master=analysisCurrentFrame, text="Renew log", font=(globalFontFamily, 40), command=partial(save, True), width=500, height=100, corner_radius=25)
    renewLogButton.grid(padx=50, pady=(25, 50))

    resetButton = ctk.CTkButton(master=analysisCurrentFrame, text="Full Reset", font=(globalFontFamily, 40), command=fullReset, width=500, height=100, corner_radius=25)
    resetButton.grid(padx=50, pady=(25, 50))

    analysisCurrentFrame.grid(column = 1, row = 3, columnspan=3, padx=50, pady=(0, 50))
    if "analysisHistoryFrame" in globals() and analysisHistoryFrame in visibleFrames:
        analysisHistoryFrame.grid_forget()
        visibleFrames.remove(analysisHistoryFrame)
    if "analysisSuggestionsFrame" in globals() and analysisSuggestionsFrame in visibleFrames:
        analysisSuggestionsFrame.grid_forget()
        visibleFrames.remove(analysisSuggestionsFrame)

def analyzeMacroText(macro):
    percentage = round((user.count(macro) / user.componentGoals[macro]) * 100, 1)
    analyzeText = None
    if (percentage > 115):
        analyzeText = ("You've exceeded your daily " + macro + " by " + str(round(percentage - 100,1)) + "%, which is " + str(round(user.count(macro) - user.componentGoals[macro], 1)) + " grams. Highest " + macro + " food: " + user.findHighest(macro).name + " (" + str(getattr(user.findHighest(macro), macro)) + " " + getUnits(macro) + ")")
    elif (percentage < 85):
        analyzeText = ("You were under your daily " + macro + " by " + str(round(100 - percentage, 1)) + "%, which is " + str(round(user.componentGoals[macro] - user.count(macro), 1)) + " grams.")
    else:
        analyzeText = ("You met your daily " + macro + " requirements, at " + str(percentage) + "% of the target. Highest " + macro + " food: " + user.findHighest(macro).name)
    return analyzeText

def analysisHistory():
    global analysisHistoryFrame
    if "analysisHistoryFrame" in globals() and analysisHistoryFrame in visibleFrames:
        return
    analysisHistoryFrame = ctk.CTkFrame(master=analysisFrame, corner_radius=25, width=1000, height=498)
    visibleFrames.append(analysisHistoryFrame)

    with open('userHistory.json') as historyFile:
        historyLogs = json.load(historyFile)
        if len(historyLogs) == 0:
            graphEmptyLabel = ctk.CTkLabel(master = analysisHistoryFrame, text="Your history is empty.", font=(globalFontFamily, 50))
            graphEmptyLabel.grid(column=1, row=1, rowspan=6, padx=300, pady=200)
            analysisHistoryFrame.grid(column = 1, row = 3, columnspan=3, padx=50, pady=(0, 43))

            if "analysisCurrentFrame" in globals() and analysisCurrentFrame in visibleFrames:
                analysisCurrentFrame.configure(width=0)
                analysisCurrentFrame.configure(height=0)
                visibleFrames.remove(analysisCurrentFrame)
            if "analysisSuggestionsFrame" in globals() and analysisSuggestionsFrame in visibleFrames:
                analysisSuggestionsFrame.grid_forget()
                visibleFrames.remove(analysisSuggestionsFrame)
            
            return

    displayAnalysisGraph("calories")

    buttonsFrame = ctk.CTkFrame(master=analysisHistoryFrame, corner_radius=25)
    for i in range(6):
        component = ["calories", "sugar", "protein", "fat", "carbs", "fiber"][i]
        componentButton = ctk.CTkButton(master=buttonsFrame, width=100, height=35, command=partial(displayAnalysisGraph, component), corner_radius=25, text=component.capitalize(), font=(globalFontFamily, 25))

        if component == "calories":
            componentButton.grid(row=2, column = i, padx=(30, 15), pady=30)
        elif component == "fiber":
            componentButton.grid(row=2, column = i, padx=(15, 30), pady=30)
        else:
            componentButton.grid(row=2, column = i, padx=(15, 15), pady=30)

    global infoLabel
    infoLabel = ctk.CTkLabel(master=analysisHistoryFrame, text="Log info will show here", font=(globalFontFamily, 40), wraplength=350)
    infoLabel.grid(row=1, column=2, padx=80)

    analysisHistoryFrame.grid(column = 1, row = 3, columnspan=3, padx=50, pady=(0, 43))
    buttonsFrame.grid(row=2, column=1, columnspan=2)

    # destroy the other frames
    if "analysisCurrentFrame" in globals() and analysisCurrentFrame in visibleFrames:
        analysisCurrentFrame.configure(width=0)
        analysisCurrentFrame.configure(height=0)
        visibleFrames.remove(analysisCurrentFrame)
    if "analysisSuggestionsFrame" in globals() and analysisSuggestionsFrame in visibleFrames:
        analysisSuggestionsFrame.grid_forget()
        visibleFrames.remove(analysisSuggestionsFrame)

def displayAnalysisGraph(component):
    global graphFrame
    graphFrame = ctk.CTkFrame(master=analysisHistoryFrame, corner_radius=25, width=650, height=350)
    with open('userHistory.json') as historyFile:
        historyLogs = json.load(historyFile)
        if len(historyLogs) > 20:
            historyLogs = historyLogs[len(historyLogs)-20:]
        for i in range(len(historyLogs)):
            logDict = historyLogs[i]
            buttonText = logDict["date"][5:7] + "\n" + logDict["date"][8:]
            createGraphColumn(logDict[component]/user.componentGoals[component]/1.5, len(historyLogs), i+1, buttonText, log=logDict)

    label150 = ctk.CTkLabel(master=analysisHistoryFrame, text = "150 %", font = (globalFontFamily, 25), wraplength=150)
    label150.place(relx=0.02, rely=0.06)

    label100 = ctk.CTkLabel(master=analysisHistoryFrame, text = "100 %", font = (globalFontFamily, 25), wraplength=150)
    label100.place(relx=0.01, rely=0.27)

    label50 = ctk.CTkLabel(master=analysisHistoryFrame, text = "50 %", font = (globalFontFamily, 25), wraplength=150)
    label50.place(relx=0.02, rely=0.48)

    label0 = ctk.CTkLabel(master=analysisHistoryFrame, text = "0 %", font = (globalFontFamily, 25), wraplength=150)
    label0.place(relx=0.025, rely=0.72)
    
    graphFrame.grid(column=1, row=1, padx=(150, 0), pady=(50, 0))

def createGraphColumn(progress, numOfLogs, columnNum, buttonText, log):
    graphProgressBar = ctk.CTkProgressBar(master=graphFrame, width=500/numOfLogs, orientation="vertical", height=400, corner_radius=5)
    graphProgressBar.set(progress)
    graphProgressBar.grid(column=columnNum, row=1)

    graphButton = ctk.CTkButton(master=graphFrame, height=50, width=500/numOfLogs, font=(globalFontFamily, 20), text=buttonText, command=partial(displayHistoryInfo, log))
    graphButton.grid(column=columnNum, row=2)

def displayHistoryInfo(log):
    infoText = ("Date: " + log["date"] + 
                "\nCalories: " + str(log["calories"]) + " kcal" +
                "\nSugar: " + str(log["sugar"]) + " grams" +
                "\nProtein: " + str(log["protein"]) + " grams" +
                "\nFat: " + str(log["fat"]) + " grams" +
                "\nCarbs: " + str(log["carbs"]) + " grams" +
                "\nFiber: " + str(log["fiber"]) + " grams")
    infoLabel.configure(text = infoText)

def analysisSuggestions():
    global analysisSuggestionsFrame
    if "analysisSuggestionsFrame" in globals() and analysisSuggestionsFrame in visibleFrames:
        return
    
    analysisSuggestionsFrame = ctk.CTkScrollableFrame(master=analysisFrame, corner_radius=25, width=1000, height=500)
    visibleFrames.append(analysisSuggestionsFrame)

    nutritionLabel = ctk.CTkLabel(master=analysisSuggestionsFrame, text=gptSuggestion["nutrition"], font=(globalFontFamily, 30), wraplength=900)
    nutritionLabel.pack(pady=50, padx=50)

    activityLabel = ctk.CTkLabel(master=analysisSuggestionsFrame, text=gptSuggestion["activities"], font=(globalFontFamily, 30), wraplength=900)
    activityLabel.pack(pady=50, padx=50)

    analysisSuggestionsFrame.grid(column = 1, row = 3, columnspan=3, padx=50, pady=(0, 50))

    if "analysisCurrentFrame" in globals() and analysisCurrentFrame in visibleFrames:
        analysisCurrentFrame.configure(width=0)
        analysisCurrentFrame.configure(height=0)
        visibleFrames.remove(analysisCurrentFrame)
    if "analysisHistoryFrame" in globals() and analysisHistoryFrame in visibleFrames:
        analysisHistoryFrame.grid_forget()
        visibleFrames.remove(analysisHistoryFrame)

def getSuggestionGPT() -> dict:
    macroInfo = ""
    for macro in ["calories", "sugar", "protein", "fat", "carbs", "fiber"]:
        macroInfo += analyzeMacroText(macro)
    prompt = (macroInfo + "State what you can expect to happen health-wise for each macro, under 10 words each ' - macro_name': expectations. Titled 'Macros'. Options: " + str(sasFoods) + ", 3 best and 3 to avoid for this individual to help meet the guidelines (e.g. if sugar is high, say to avoid high sugar foods), around 30 words. Titled 'Nutrition Advice'. Then, give recommendations for activities, around 30 words, bullet points. Titled 'Activities Advice'.")
    response = gpt.askGPT(prompt)

    while response.find("*") != -1:
        response = response.replace("*", "")
    while response.find("#") != -1:
        response = response.replace("#", "")

    responseDict = {}
    for i in range(6) :
        macros = ["calories", "sugar", "protein", "fat", "carbs", "fiber"]
        if i == 5:
            responseDict[macros[i]] = response[response.find(macros[i].capitalize() + ":"):response.find("Nutrition Advice")]
        else:
            responseDict[macros[i]] = response[response.find(macros[i].capitalize() + ":"):response.find(macros[i+1].capitalize() + ":") - 2]

    responseDict["nutrition"] = response[response.find("Nutrition Advice"):response.find("Activities Advice")]
    if response.find("Activities Advice"):
        responseDict["activities"] = response[response.find("Activities Advice"):]

    return responseDict

def displayEnter():
    global enterFrame
    menuFrame.destroy()
    enterFrame = ctk.CTkFrame(master=root, corner_radius=25)
    enterFrame.place(relx=0.5, rely=0.5, anchor="center")

    backIcon = ctk.CTkImage(light_image=Image.open("assets/back.png"), size=(30, 30))
    enterBackButton = ctk.CTkButton(master=enterFrame, image=backIcon, text="Back", width=40, height=40, command=displayMenu)
    enterBackButton.place(relx=0.07, rely=0.12, anchor = "center")

    titleLabel = ctk.CTkLabel(master=enterFrame, text="Enter a new food", font=(globalFontFamily, 50))
    titleLabel.grid(column=2, row=1, padx=30, pady=50)

    global foodNameBox
    foodNameLabel = ctk.CTkLabel(master=enterFrame, font=(globalFontFamily, 30), text="Name of food:")
    foodNameLabel.grid(column=1, row=2, padx=30, pady=20)
    foodNameBox = ctk.CTkEntry(master=enterFrame, font=(globalFontFamily, 30), width=250, height=80, justify="center", corner_radius=25)
    foodNameBox.grid(column=1, row=3, padx=30, pady=30)

    global foodAmountBox
    foodAmountLabel = ctk.CTkLabel(master=enterFrame, font=(globalFontFamily, 30), text="Amount of food:")
    foodAmountLabel.grid(column=2, row=2, padx=30, pady=20)
    foodAmountBox = ctk.CTkEntry(master=enterFrame, font=(globalFontFamily, 30), width=250, height=80, justify="center", corner_radius=25)
    foodAmountBox.grid(column=2, row=3, padx=30, pady=30)

    global foodUnitSelect
    foodUnitLabel = ctk.CTkLabel(master=enterFrame, font=(globalFontFamily, 30), text="Units:")
    foodUnitLabel.grid(column=3, row=2, padx=30, pady=20)
    foodUnitSelect = ctk.CTkComboBox(master=enterFrame, font=(globalFontFamily, 30), values=["Number", "Grams", "Cups"], width=250, height=80, justify="center", corner_radius=25)
    foodUnitSelect.grid(column=3, row=3, padx=30, pady=30)

    enterButton = ctk.CTkButton(master=enterFrame, text="Enter", width=400, height=75, font=(globalFontFamily, 30), command=partial(foodEntered), corner_radius=25)
    enterButton.grid(column=1, row=4, padx=400, pady=(50, 100), columnspan=3)

def displayLog():
    menuFrame.destroy()
    global logFrame
    logFrame = ctk.CTkFrame(master=root, corner_radius=25, width=800)
    logFrame.place(relx=0.5, rely=0.5, anchor="center")
    displayLogTotals()

    logLabel = ctk.CTkLabel(master=logFrame, text="Your log", font=(globalFontFamily, 50))
    logLabel.grid(column = 1, row = 1, columnspan = 2, padx=600, pady=50)

    totalsButton = ctk.CTkButton(master=logFrame, text="View totals", font=(globalFontFamily, 25), command=displayLogTotals, corner_radius=25, width=200, height=50)
    totalsButton.grid(column=1, row=2, padx=30, pady=(10, 0))

    foodsButton = ctk.CTkButton(master=logFrame, text="View foods", font=(globalFontFamily, 25), command=displayLogFoods, corner_radius=25, width=200, height=50)
    foodsButton.grid(column=2, row=2, padx=30, pady=(10, 0))

    backIcon = ctk.CTkImage(light_image=Image.open("assets/back.png"), size=(30, 30))
    logBackButton = ctk.CTkButton(master=logFrame, image=backIcon, text="Back", width=40, height=40, command=displayMenu)
    logBackButton.place(relx = 0.03, rely = 0.08)

def save(isDone):
    with open('userHistory.json') as historyFile:
        historyLogs = json.load(historyFile)
        logDictionary = user.getNutrition()
        logDictionary["done"] = isDone
        logDictionary["foodsArr"] = user.getSerializableArr()
        logDictionary["date"] = str(date.today())

        if len(historyLogs) == 0 or historyLogs[len(historyLogs) - 1]["done"]:
            historyLogs.append(logDictionary)
        else:
            historyLogs[len(historyLogs) - 1] = logDictionary

        jsonObject = json.dumps(historyLogs)
        with open("userHistory.json", "w") as outfile:
            outfile.write(jsonObject)
    
    user.foodsArr = []

def displayLogTotals():
    global logTotalsFrame
    if "logTotalsFrame" in globals() and logTotalsFrame in visibleFrames:
        return

    logTotalsFrame = ctk.CTkFrame(master=logFrame, corner_radius=25)
    visibleFrames.append(logTotalsFrame)

    createProgressBar("calories", 1)
    createProgressBar("sugar", 2)
    createProgressBar("protein", 3)
    createProgressBar("fat", 4)
    createProgressBar("carbs", 5)
    createProgressBar("fiber", 6)

    logTotalsFrame.grid(column = 1, row=3, columnspan=2, padx=30, pady=(0, 50), ipady=25)
    if "logFoodsFrame" in globals() and logFoodsFrame in visibleFrames:
        logFoodsFrame.destroy()
        visibleFrames.remove(logFoodsFrame)

def createProgressBar(component, gridRow):
    progressBar = ctk.CTkProgressBar(master=logTotalsFrame, orientation="horizontal", height=30, width=400)
    progressVar = user.count(component)/user.componentGoals[component]
    if (progressVar <= 1):
        progressBar.set(progressVar)
    else:
        progressBar.set(1)
        progressBar.configure(progress_color="red")

    componentText = ctk.CTkLabel(master=logTotalsFrame, text=component.capitalize(), font=(globalFontFamily, 30))

    additionalText = {
        "calories": " (maintenance)",
        "sugar": " (maximum)",
        "protein": "",
        "fat": "",
        "carbs": "",
        "fiber": ""
    }

    progressText = str(user.count(component)) + " / " + str(user.componentGoals[component]) + " " + getUnits(component) + additionalText[component]
    progressLabel = ctk.CTkLabel(master=logTotalsFrame, text=progressText, font=(globalFontFamily, 30))

    if component == "calories":
        componentText.grid(column=1, row=gridRow, padx=30, pady=(50, 15))
        progressBar.grid(column=2, row=gridRow, padx=30, pady=(50, 15))
        progressLabel.grid(column=3, row=gridRow, padx=30, pady=(50, 15))
    else:
        componentText.grid(column=1, row=gridRow, padx=30, pady=15)
        progressBar.grid(column=2, row=gridRow, padx=30, pady=15)
        progressLabel.grid(column=3, row=gridRow, padx=30, pady=15)

def displayLogFoods():
    global logFoodsFrame
    if "logFoodsFrame" in globals() and logFoodsFrame in visibleFrames:
        return

    logFoodsFrame = ctk.CTkFrame(master=logFrame, corner_radius=25, width=800)
    visibleFrames.append(logFoodsFrame)

    foodsLabel = ctk.CTkLabel(master=logFoodsFrame, font=(globalFontFamily, 40), text="Foods Added")
    foodsLabel.grid(column=1, row=1, padx=300, pady=50, columnspan=2)
    
    if len(user.foodsArr) == 0:
        emptyLabel = ctk.CTkLabel(master=logFoodsFrame, text="Your log is empty.", font=(globalFontFamily, 30))
        emptyLabel.grid(column=1, row=2, padx=200, pady=(100, 150), columnspan=2)
        
        logFoodsFrame.grid(column = 1, row=3, columnspan=2, padx=100, pady=(0, 50))
        if "logTotalsFrame" in globals() and logTotalsFrame in visibleFrames:
            logTotalsFrame.destroy()
            visibleFrames.remove(logTotalsFrame)
        return
    
    foodList = ctk.CTkScrollableFrame(master=logFoodsFrame, corner_radius=25, width=500, height=400)
    foodList.grid(column=1, row=3, padx = (100, 0), pady=(0, 50))

    global foodInfoFrame
    foodInfoFrame = ctk.CTkFrame(master=logFoodsFrame, corner_radius=25, width=600)
    foodInfoFrame.grid(column = 2, row=3, padx=50, pady=(0, 80))

    foodInfoLabel = ctk.CTkLabel(master=foodInfoFrame, text="Info will display here", font=(globalFontFamily, 30), height=200)
    foodInfoLabel.grid(padx=30, pady=30)

    for food in user.foodsArr:
        foodButtonText = food.name.capitalize()
        foodButton = ctk.CTkButton(master=foodList, text=foodButtonText, command=partial(foodButtonPressed, food, foodInfoLabel), font=(globalFontFamily, 30), corner_radius=25, width=480, height=70)
        foodButton.grid(pady=20)
    
    global deleteFoodButton
    deleteFoodButton = ctk.CTkButton(master=foodInfoFrame, text="Delete from log", command=partial(deleteFood, food), font=(globalFontFamily, 30), width=300, height=75, corner_radius=25)
    deleteFoodButton.grid(pady = (0, 30), padx=100)

    logFoodsFrame.grid(column = 1, row=3, columnspan=2, padx=100, pady=(0, 50))
    if "logTotalsFrame" in globals() and logTotalsFrame in visibleFrames:
        logTotalsFrame.destroy()
        visibleFrames.remove(logTotalsFrame)

def foodButtonPressed(food, foodInfoLabel):
    foodInfoLabel.configure(text="Name: " + food.name.capitalize() + 
                                 "\nCalories: " + str(food.calories) +
                                 "\nSugar: " + str(food.sugar) + " grams" +
                                 "\nProtein: " + str(food.protein) + " grams" + 
                                 "\nFat: " + str(food.fat) + " grams" + 
                                 "\n Carbs: " + str(food.carbs) + " grams" + 
                                 "\n Fiber: " + str(food.fiber) + " grams")
    deleteFoodButton.configure(command=partial(deleteFood, food))

def deleteFood(foodToDelete):
    if foodToDelete in user.foodsArr:
        oldFoodsFrame = logFoodsFrame
        user.foodsArr.remove(foodToDelete)
        visibleFrames.remove(logFoodsFrame)
        visibleFrames.append(logTotalsFrame)
        displayLogFoods()
        oldFoodsFrame.destroy()

def foodEntered():
    successful = newFood()
    global resultFrame
    resultFrame = ctk.CTkFrame(master=root, corner_radius=25)
    resultFrame.place(relx=0.5, rely=0.5, anchor="center")
    
    if successful:
        successLabel = ctk.CTkLabel(master=resultFrame, text="Your food has been successfully added to the log.", font=(globalFontFamily, 50))
        successLabel.grid(column=1, row=1, padx=50, pady=50, columnspan=2)

        okButton = ctk.CTkButton(master=resultFrame, text="Ok", font=(globalFontFamily, 30), width=400, height=75, command=destroyResultFrame, corner_radius=25)
        okButton.grid(column=1, row=2, padx=50, pady=50)

        viewButton = ctk.CTkButton(master=resultFrame, text="View details", font=(globalFontFamily, 30), width=400, height=75, command=viewFoodDetails, corner_radius=25)
        viewButton.grid(column=2, row=2, padx=50, pady=50)
    else:
        successLabel = ctk.CTkLabel(master=resultFrame, text="Something went wrong. Please check your responses or try again.", font=(globalFontFamily, 50))
        successLabel.grid(column=2, row=1, padx=50, pady=50, columnspan=2)

        okButton = ctk.CTkButton(master=resultFrame, text="Ok", font=(globalFontFamily, 30), width=400, height=75, command=destroyResultFrame, corner_radius=25)
        okButton.grid(column=2, row=2, padx=50, pady=50, columnspan=2)

def newFood() -> bool: # returns whether or not it was successful
    newFood = Food("", 0, 0, 0, 0, 0, 0)

    prompt = "Find an estimate of the number of calories (kcal), sugar (g), protein (g), fat (g), carbs (g), and fiber (g) in " + foodAmountBox.get() + " " + foodUnitSelect.get() + " of " + foodNameBox.get() + ". Return ONLY a python dictionary (without stating anything at the front) with the name of each component as the key, all lowercase. Make each value a number. Type it as just text, not code. Do not include the units in the key, and do not include comments in the code. Return ONLY the dictionary, do not provide additional commentary or comments."
    gptResponse = gpt.askGPT(prompt)
    if not evalable(gptResponse):
        return False
    
    newFood.name = foodNameBox.get()
    foodComponents = eval(gptResponse)
    for component in foodComponents:
        if getattr(newFood, component, "None") != "None":
            setattr(newFood, component, foodComponents[component])
    user.addFood(newFood)
    return True

def viewFoodDetails():
    recentFood = user.foodsArr[len(user.foodsArr) - 1]
    destroyResultFrame()

    global viewFrame
    viewFrame = ctk.CTkFrame(master=root, corner_radius=25)
    viewFrame.place(relx=0.5, rely=0.5, anchor="center")

    foodInfo = ("Name: " + recentFood.name.capitalize() + 
                "\nCalories: " + str(recentFood.calories) +
                "\nSugar: " + str(recentFood.sugar) + " grams" +
                "\nProtein: " + str(recentFood.protein) + " grams" + 
                "\nFat: " + str(recentFood.fat) + " grams" + 
                "\nCarbs: " + str(recentFood.carbs) + " grams" + 
                "\nFiber: " + str(recentFood.fiber) + " grams")
    newLabel = ctk.CTkLabel(master=viewFrame, text=foodInfo, font=(globalFontFamily, 40))
    newLabel.pack(padx=30, pady=30)
    
    okButton = ctk.CTkButton(master=viewFrame, text="Ok", font=(globalFontFamily, 30), width=400, height=75, command=destroyViewFrame, corner_radius=25)
    okButton.pack(padx=50, pady=50)

def evalable(given) -> bool:
    try:
        eval(given)
    except:
        return False
    else:
        return True

def destroyResultFrame():
    resultFrame.destroy()
    
def destroyViewFrame():
    viewFrame.destroy()

def getUnits(component):
    units = {
        "name": "",
        "calories": "kcal",
        "sugar": "grams",
        "protein": "grams",
        "fat": "grams",
        "carbs": "grams",
        "fiber": "grams"
    }
    if (units[component]):
        return units[component]
    return "grams"

def fullReset():
    with open("userHistory.json", "w") as historyFile:
        emptyArray = json.dumps([])
        historyFile.write(emptyArray)
    with open("userInfo.json", "w") as infoFile:
        resetDict = json.dumps({"maintenanceCalories": 0})
        infoFile.write(resetDict)

root.mainloop()