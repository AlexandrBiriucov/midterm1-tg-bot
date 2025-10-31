import sys
sys.path.append(r"C:\telegram_gym_bot\main\feature\dev1_workout_tracking")

#from main import dp (катастрофа)
#from db import SessionLocal
#from models import Workout


from ..dev1_workout_tracking.db import SessionLocal, init_db
from ..dev1_workout_tracking.models import Workout
from .stats_models import User_Stats
import asyncio
from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup,Message,KeyboardButton
from datetime import datetime , timezone, timedelta
from sqlalchemy import select
from collections import defaultdict
import matplotlib.pyplot as plt
import os
from aiogram.types import FSInputFile
#creation of the router and storage for the ISM
stats_router = Router()
storage = MemoryStorage()
stats_router.storage = storage 



#defining FSM
class StatsForm(StatesGroup):
    choice_type=State()
    time_period=State()
    progression_state=State()
    best_lift=State()
    best_lift_action=State()
    volume=State()
    consistency=State()

#hander for the stats command 
# @stats_router.message(Command("stats"))
# async def stats_comand(message: types.Message, state:FSMContext):
#     keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add("Bench","Squat")
#     await message.answer("Which exercise do you want stats for?", reply_markup=keyboard)
#     await state.set_state(StatsForm.exercise_type)

#start of the stats command and FSM dialog logic
@stats_router.message(Command("statistics"))
async def stats_command(message: Message, state: FSMContext):
    await state.set_state(StatsForm.choice_type)
    await message.answer(
        "What stats do u want to see?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Overall"), KeyboardButton(text="Progression")],
                [KeyboardButton(text="Leaderboard"), KeyboardButton(text="Achievements")]
            ],
            resize_keyboard=True,
        ),
    )

#user chooses overall option 
@stats_router.message(StatsForm.choice_type, F.text.casefold() == "overall")#might need to change to lover case(done)
async def process_overall_choice(message:Message,state:FSMContext):
    await state.update_data(choice_type="overall")
    await state.set_state(StatsForm.time_period)
    await message.answer(
        "Choose the time period of the stats",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Today")],
                [KeyboardButton(text="This Week")],
                [KeyboardButton(text="All Time")]
            ],
            resize_keyboard=True,
        ),
                         
    )



#PROGRESSION BUTTON
@stats_router.message(StatsForm.choice_type,F.text.casefold()=="progression")
async def process_progression_choice(message:Message,state:FSMContext):
    await state.update_data(choice_type="progression")
    await state.set_state(StatsForm.progression_state)
    await message.answer(
        "Choose the progression",
        reply_markup=ReplyKeyboardMarkup(

            keyboard=[

                [KeyboardButton(text="Best Lift Progression")],
                [KeyboardButton(text="Volume Progression")],
                [KeyboardButton(text="Consistency")]

                ],
            resize_keyboard=True,
        ),


 
    )
#user choose best_lift route
@stats_router.message(StatsForm.progression_state, F.text.casefold()=="best lift progression")
async def process_best_lift(message:types.Message,state:FSMContext):
   # data=await state.get_data() 
   # #choice_type=data.get("choice_type")
    await state.update_data(progression="best_lift")
    await state.set_state(StatsForm.best_lift)
    await message.answer(
        "Which exercise do u want to choose?"
        "Please write the exercise name (BenchPress, Squat, Deadlift..)"


    ) 



@stats_router.message(StatsForm.best_lift)      
async def process_best_lift_exercise_choice(message:Message, state: FSMContext):
    exercise=message.text.strip()

    await state.update_data(exercise=exercise)
    user_id=message.from_user.id
    session=SessionLocal()
    
#get max values of the exercise then show how i
# t grows by weeks and shit, the show the theoretical 
# max value using the one rep max fomula and als o

#######(add the control for  case when there is no data to work with for some exercise )

    try:
        results = (
            session.query(Workout)
            .filter(Workout.user_id == user_id, Workout.exercise.ilike(exercise))
            .order_by(Workout.created_at.asc())
            .all()
                )
#this part i couldnt do myself chatgpt was abused heavily
        weekly_max = defaultdict(int)  

        for w in results:
            week_start = w.created_at - timedelta(days=w.created_at.weekday())  
            weekly_max[week_start] = max(weekly_max[week_start], w.weight)

    
        # for  w in weekly_max:  (tried to do the printing myself it didtn worked)
        #     text= "\n".join (
        #         f"week {weekly_max} best result was {weekly_max[w]}kg"
        #     )
        # await message.answer("here is your week by week progression:\n")

        #version2 
        
        
        
        lines=[]


        for week_start,max_weight in weekly_max.items():
            week_str = week_start.strftime("%Y-%m-%d")  # Monday of the week
            lines.append(f"Week starting {week_str}: best result was {max_weight} kg")

        text="\n".join(lines)
        await message.answer(f"Here is your weekly progression:\n{text}")
        await state.update_data(weekly_max={str(k): v for k, v in weekly_max.items()})
        await state.set_state(StatsForm.best_lift_action)

        await message.answer("If you want to see the graph of your week by week progress type 'graph' ,type 'orm' to look up ur theoretical" \
        " OneRepMax using Brzycki formula or return to the main stats page by typing 'back' ")


        
    

    finally:
        session.close()
    #     await state.set_state(StatsForm.choice_type)
    #     await message.answer(
    #     "What stats do u want to see?",
    #     reply_markup=ReplyKeyboardMarkup(
    #         keyboard=[
    #             [KeyboardButton(text="Overall"), KeyboardButton(text="Progression")],
    #             [KeyboardButton(text="Leaderboard"), KeyboardButton(text="Achievements")]
    #         ],
    #         resize_keyboard=True,
    #     ),
    # )






@stats_router.message(StatsForm.best_lift_action)
async def ending_the_bestlift_state(message:types.Message,state:FSMContext):
    await state.set_state(StatsForm.best_lift_action)
    sup_choice=message.text.strip()
    #add set state if needed
    if sup_choice.lower()=="graph":
        data= await state.get_data()
        weekly_max={datetime.fromisoformat(k): v for k,v in data.get("weekly_max",{}).items()}
        weeks = list(weekly_max.keys())
        weights = list(weekly_max.values())
        plt.plot(weeks, weights, marker="o")
        plt.title("Best Lift Progression")
        plt.xlabel("Week")
        plt.ylabel("Max Weight (kg)")
        plt.tight_layout()
        plt.savefig("progress.png")
        plt.close()

        photo = FSInputFile("progress.png")
        await message.answer_photo(photo, caption="Your weekly progression graph")

        


        #might need this for cleanup
        #os.remove("progress.png")

        

    




    





#after overall user can choose the time period of the stats
@stats_router.message(StatsForm.time_period)
async def process_time_period(message :types.Message, state:FSMContext):
    data= await state.get_data()
    
    choice_type=data.get("choice_type")
    time_period=message.text.strip()

    user_id=message.from_user.id
    now=datetime.now(timezone.utc)
    session=SessionLocal()

    try:
        q=select(Workout).where(Workout.user_id==user_id)

        if time_period=="Today":
             start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
             q=q.where(Workout.created_at>=start , Workout.created_at<=now)
        elif time_period=="This Week":
            start=now-timedelta(days=7)
            q=q.where(Workout.created_at>=start,Workout.created_at<=now)
        
        q=q.order_by(Workout.created_at.desc())
        results= session.execute(q).scalars().all()
        if not results:
            await message.answer("no results found")
        else:
            text = "\n".join(
                f"{w.created_at:%d-%m %H:%M} — {w.exercise} {w.sets}x{w.reps}x{w.weight} kg"
                for w in results
            )
            
            await message.answer(f"Here are your workouts:\n{text}")


        await state.set_state(StatsForm.choice_type)
        await message.answer(
            "What stats do you want to see next?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Overall"), KeyboardButton(text="Progression")],
                    [KeyboardButton(text="Leaderboard"), KeyboardButton(text="Recent Workouts")],
                    [KeyboardButton(text="Achievements"), KeyboardButton(text="Breakdown")],
                ],
                resize_keyboard=True,
            )
        )

    finally:
        session.close()
        

















# @stats_router.message(StatsForm.exercise_type)
# async def process_exercise_choice(message: types.Message, state: FSMContext):
#     exercise = message.text.strip()

#     if exercise.lower() == "bench":
#         await message.answer("You chose Bench Press 🏋️‍♂️")
#     elif exercise.lower() == "squat":
#         await message.answer("You chose Squat 🏋️‍♀️")
#     else:
#         await message.answer("Unknown exercise. Please choose from the keyboard!")

#     # end the FSM flow
#     await state.clear()





# db = SessionLocal()

# # Fetch all workouts
# workouts = db.query(Workout).all()

# for w in workouts:
#     print(w.exercise)  

# db.close()



