import sys,calendar
sys.path.append(r"C:\telegram_gym_bot\main\feature\dev1_workout_tracking")
import matplotlib.dates as mdates
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
from aiogram.types import ReplyKeyboardMarkup,Message,KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardRemove
from datetime import datetime , timezone, timedelta
from sqlalchemy import select
from collections import defaultdict
import matplotlib.pyplot as plt
import os
from aiogram.types import FSInputFile
from .utils_funcs import one_rep_max,calculate_volume
# from .muscle_groups import exercise_to_muscle
import pandas as pd
import seaborn as sns
#creation of the router and storage for the ISM
stats_router = Router()
storage = MemoryStorage()
stats_router.storage = storage 


#####
#later:

#end of the state flow, might need to chagne to lambda
#  m bulsshit instead of simple text.casefold==

####






#defining FSM
class StatsForm(StatesGroup):
    choice_type=State()
    time_period=State()
    progression_state=State()
    best_lift=State()
    best_lift_action=State()
    volume_state=State()
    consistency=State()
    leaderboard_state=State()
    chart_state=State()
    muscle_grp_period=State()
    muscle_grp_process_period=State()
    muscle_grp_state=State()
    heat_map_state=State()
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
                [KeyboardButton(text="Overall")],
                 [ KeyboardButton(text="Progression")]
                # [KeyboardButton(text="Leaderboard"), KeyboardButton(text="Achievements")]
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
                [KeyboardButton(text="Muscle Group Distribution")],
                [KeyboardButton(text="Heat Map")]
                ],
            resize_keyboard=True,
        ),


 
    )




#leaderboard
# @stats_router.message(StatsForm.choice_type,F.text.casefold()=="leaderboard")
# async def process_leaderboard_choice(meesage: types.Message,state:FSMContext):
#     await state.set_state(StatsForm.leaderboard_state)
    

















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

        weekly_max = defaultdict(int)  

        for w in results:
            week_start = (w.created_at - timedelta(days=w.created_at.weekday())).date()  
            weekly_max[week_start] = max(weekly_max[week_start], w.weight)

         
        lines=[]


        for week_start,max_weight in weekly_max.items():
            week_str = week_start.strftime("%Y-%m-%d")  # Monday of the week
            lines.append(f"Week starting {week_str}: best result was {max_weight} kg")

        text="\n".join(lines)
        await message.answer(f"Here is your weekly progression:\n{text}")
        await state.update_data(weekly_max={str(k): v for k, v in weekly_max.items()})
        await state.set_state(StatsForm.best_lift_action)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Grpah", callback_data="graph")],
                [InlineKeyboardButton(text="One Repetition Max", callback_data="orm")],
                [InlineKeyboardButton(text="Previous", callback_data="Back")],
               
            ])
        await message.answer("Choose an option",reply_markup=keyboard)

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






@stats_router.callback_query(F.data.in_(["graph", "orm", "Back"]))
async def graph_or_ORM(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data
    await callback.answer()  # acknowledge the click so Telegram stops the loading animation

    if choice == "graph":
        data = await state.get_data()
        weekly_max = {datetime.fromisoformat(k): v for k, v in data.get("weekly_max", {}).items()}
        weeks = list(weekly_max.keys())
        weights = list(weekly_max.values())

        if not weeks:
            await callback.message.answer("No weekly data available to display.")
            return

        plt.plot(weeks, weights, marker="o", linestyle="-", color="blue")
        plt.xticks(rotation=45, ha="right", fontsize=10)
        plt.title("Best Lift Progression")
        plt.xlabel("Week")
        plt.ylabel("Max Weight (kg)")
        plt.tight_layout()
        plt.savefig("progress.png")
        plt.close()

        photo = FSInputFile("progress.png")
        await callback.message.answer_photo(photo, caption="Your weekly progression graph")

    elif choice == "orm":
        data = await state.get_data()
        user_id = callback.from_user.id
        exercise_choice = data.get("exercise")
        session = SessionLocal()

        try:
            results = (
                session.query(Workout)
                .filter(Workout.user_id == user_id, Workout.exercise.ilike(exercise_choice))
                .order_by(Workout.weight.desc())
                .all()
            )

            if results:
                best_set = [one_rep_max(r.weight, r.reps) for r in results]
                best_lift = max(best_set)
                await callback.message.answer(f"Theoretically your current max weight on {exercise_choice} is {best_lift:.1f} kg")
            else:
                await callback.message.answer(f"No data registered for {exercise_choice}")
        finally:
            session.close()
            await state.clear()

    elif choice == "Back":
        await state.set_state(StatsForm.choice_type)
        # await callback.message.answer("Returning to main stats menu...")
        await callback.message.answer(
        "What stats do u want to see?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Overall")],
                 [ KeyboardButton(text="Progression")]
                # [KeyboardButton(text="Leaderboard"), KeyboardButton(text="Achievements")]
            ],
            resize_keyboard=True,
        ),
    )

#volume calculation route 
# @stats_router.message(StatsForm.progression_state,F.text.casefold()=="volume progression")
@stats_router.message(StatsForm.progression_state, lambda m: m.text.casefold() == "volume progression")

async def process_volume(message:types.Message,state:FSMContext):
    await state.set_state(StatsForm.volume_state)

    
    user_id=message.from_user.id
    session=SessionLocal()
    try:
        results=(
            session.query(Workout)
            .filter(Workout.user_id==user_id).all()  
             
             
              )
        weekly_volume= defaultdict(int)  

        for w in results:
                week_start = (w.created_at - timedelta(days=w.created_at.weekday())).date()
                weekly_volume[week_start] += calculate_volume(w.sets, w.reps, w.weight)





        await state.update_data(
            
              weekly_volume={str(k): v for k, v in weekly_volume.items()}
                        )
                     

             

        lines=[]

                
        for week_start,volume in weekly_volume.items():
            week_str = week_start.strftime("%Y-%m-%d")  # Monday of the week
            lines.append(f"The volume in the week starting at {week_str} was {volume} ")

        text="\n".join(lines)
        await message.answer(f"Here is your weekly progression:\n{text}",reply_markup=ReplyKeyboardRemove())
        #await state.update_data(weekly_max={str(k): v for k, v in weekly_max.items()})
       # await state.set_state(StatsForm.best_lift_action)

        
        # q=select(Workout).where(Workout.user_id==user_id)

        # start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        # q=q.where(Workout.created_at>=start , Workout.created_at<=now)
        
            
        await message.answer("If u want to see the volume bar charts type 'chart' ")
        await state.set_state(StatsForm.chart_state)

#         data = await state.get_data()
# weekly_volume = {datetime.fromisoformat(k): v for k, v in data["weekly_volume"].items()}



    finally:
        session.close()










# @stats_router.message(StatsForm.chart_state)
# async def process_chart(message:types.Message,state:FSMContext):
#     data=await state.get_data()
#     data_for_chart={datetime.fromisoformat(k):v for k,v in data.get("weekly_volume",{}).items()}
#     weeks=list(data_for_chart.keys())
#     volumes=list(data_for_chart.values())
#     plt.bar(weeks,volumes,width=0.5)
#     plt.xticks(rotation=45,ha="right",fontsize=10)
#     plt.title("Volume Progression")
#     plt.xlabel("Week")
#     plt.ylabel("Volume")
#     plt.tight_layout()
#     plt.savefig("volume_progress.png")
#     plt.close
#     photo=FSInputFile("volume_progress.png")
#     await  message.answer_photo(photo,caption="Your weekly volume progression")
#     #add await set state get back to the statistics menu




@stats_router.message(StatsForm.chart_state)
async def process_chart(message:types.Message,state:FSMContext):
    data = await state.get_data()
    data_for_chart = {datetime.fromisoformat(k): v for k, v in data.get("weekly_volume", {}).items()}
    weeks = list(data_for_chart.keys())
    volumes = list(data_for_chart.values())

    # import matplotlib.dates as mdates
    # import pandas as pd

    plt.figure(figsize=(6,4))

    if len(weeks) <= 2:
        plt.plot(weeks, volumes, marker="o", linestyle="-")
        plt.xlim(weeks[0] - pd.Timedelta(days=1), weeks[-1] + pd.Timedelta(days=1))
    else:
        plt.bar(weeks, volumes, width=0.5)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.title("Volume Progression")
    plt.xlabel("Week")
    plt.ylabel("Volume")
    plt.tight_layout()
    plt.savefig("volume_progress.png")
    plt.close()

    photo = FSInputFile("volume_progress.png")
    await message.answer_photo(photo, caption="Your weekly volume progression")




















#to do:
#this bs it should it give u the pie chart of the muscles groups  trained  so basscily 
#filter the exercises that a user did in some session(week,day,idk) then link to the muscle
#group and then use those muscle group percemtages in the pie char 
# from collections import defaultdict
# from datetime import datetime

@stats_router.message(StatsForm.progression_state, F.text.casefold() == "muscle group distribution")
async def process_muscle_grp_distribution(message: types.Message, state: FSMContext):
    await state.set_state(StatsForm.muscle_grp_state)
    await message.answer("Muscle Distribution Menu",reply_markup=ReplyKeyboardRemove())
    user_id = message.from_user.id
    session = SessionLocal()
    try:
        results = (
            session.query(Workout)
            .filter(Workout.user_id == user_id)
            .order_by(Workout.created_at.desc())
            .all()
        )
        if not results:
            await message.answer("No workouts found.")
            return

        # Group by date only
        workouts_by_date = defaultdict(list)
        for w in results:
            workout_date = w.created_at.date()  # e.g. 2025-09-13
            workouts_by_date[workout_date].append(w)

        # Build keyboard with one button per date
        keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{date:%d-%m-%Y} — {len(workouts_by_date[date])} exercises",
                        callback_data=f"workout_{date}"
                    )
                ]
                for date in sorted(workouts_by_date.keys(), reverse=True)
            ]
        )

       

        await message.answer("Select a workout date to see muscle distribution:", reply_markup=keyboard)


    finally:
        session.close()


@stats_router.callback_query(lambda c: c.data.startswith("workout_"))
async def workout_selected(callback_query: types.CallbackQuery):
    date_str = callback_query.data.split("_")[1]
    workout_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    session = SessionLocal()
    try:
        # Fetch all exercises from that date
        workouts = (
            session.query(Workout)
            .filter(
                Workout.user_id == callback_query.from_user.id,
                Workout.created_at >= workout_date,
                Workout.created_at < workout_date + timedelta(days=1),
            )
            .all()
        )

        muscle_volume = defaultdict(int)
        for w in workouts:
            volume = w.sets * w.reps * w.weight
            muscle = exercise_to_muscle.get(w.exercise, "Other")
            muscle_volume[muscle] += volume

       
        # await callback_query.message.answer(f"Muscle distribution for {workout_date}:\n{dict(muscle_volume)}")     simple printing
       #pie plot
        labels = list(muscle_volume.keys())
        sizes = list(muscle_volume.values())
        explode = [0.1 if i == max(sizes) else 0 for i in sizes]
        fig, ax = plt.subplots()
        ax.pie(sizes,explode=explode, labels=labels, autopct="%1.1f%%",shadow=True, startangle=90)
        ax.axis("equal")

       
        filename = "muscle_distribution.png"
        plt.savefig(filename)
        plt.close(fig)


        await callback_query.message.answer_photo(photo=FSInputFile(filename))
        


    finally:
        session.close()

    




@stats_router.message(StatsForm.progression_state, F.text.casefold() == "heat map")
async def process_heat_map(message:types.Message,state:FSMContext):



    await state.set_state(StatsForm.heat_map_state)
    user_id=message.from_user.id
    session=SessionLocal()
    try:
        workouts=session.query(Workout).filter(Workout.user_id==user_id).all()
        heatmap_data=defaultdict(lambda:[0,0,0,0])
        for w in workouts:
            month=w.created_at.month
            week_of_month = min((w.created_at.day - 1) // 7, 3)
            heatmap_data[month][week_of_month]+=1
            df=pd.DataFrame.from_dict(
            heatmap_data,
            orient="index",
             columns=["Week 1", "Week 2", "Week 3", "Week 4"]
             )

        df = df.sort_index()
        df.index = df.index.map(lambda m: calendar.month_abbr[m])

        plt.figure(figsize=(8,6))
        sns.heatmap(df, annot=True, cmap="YlOrRd", cbar=True, fmt="d")
        plt.title("Workout Frequency per Month/Week")
        plt.xlabel("Week of Month")
        plt.ylabel("Month")
        filename = "heatmap.png"
        plt.savefig(filename)
        

        photo=FSInputFile("heatmap.png")
        await  message.answer_photo(photo,caption="Your week by week heatmap")
    
    finally:
        session.close()
        await state.clear()


















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
        await state.clear()        

















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