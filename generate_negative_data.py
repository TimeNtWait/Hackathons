import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# Функция опредления уровня схожести между строками (коэффициент Танимото), как альтернатива difflib
def tanimoto(s1, s2):
    if len(s1) == 0 and len(s2) == 0:
      return 0 
    a, b, c = len(s1), len(s2), 0.0
    for sym in s1:
        if sym in s2:
            c += 1
    return c / (a + b - c)


PATH_PROJECT = "for_hack_2022/"

# Кандидаты
filename_candidates = PATH_PROJECT +  "data_candidates.csv"
# данные по образованию кандидатов
filename_education = PATH_PROJECT +  "data_candidates_education.csv"
# места работы кандидатов
filename_work_places = PATH_PROJECT  + "data_candidates_work_places.csv"
# Вакансии
filename_jobs = PATH_PROJECT +  "data_jobs.csv"



candidates_df = pd.read_csv(filename_candidates, sep=";", names=['id', 'position', 'sex',   
                                                                 'citizenship',   'age', 'salary',  
                                                                 'langs', 'driver_license', 'subwey', 
                                                                 'skills', 'employment', 'shedule', 
                                                                 'candidate_region', 'date_created', 
                                                                 'job_id', 'candidate_status_id', 'status'])
education_df = pd.read_csv(filename_education, sep=";", names=['id', 'university', 'faculty', 'graduate_year'])
work_places_df = pd.read_csv(filename_work_places, sep=";", names=['id', 'work_place_position', 'from_year',  'from_month', 'to_year', 'to_month'])
jobs_df = pd.read_csv(filename_jobs, sep=";", names=['job_id', 'job_status', 'job_name',  'job_region', 'job_description'])

candidates_df.shape, education_df.shape, work_places_df.shape, jobs_df.shape


print(f"candidates_df.shape {candidates_df.shape}")
candidates_mask = candidates_df.duplicated(subset=["id", "job_id"])
candidates_df = candidates_df.loc[~candidates_mask]
print(f"candidates_df.shape {candidates_df.shape}")


local_df = pd.DataFrame()
# перечень вакансий для генерации негативных данных
jobs_for_generations = jobs_df[( (jobs_df["job_region"] == 'Москва') | (jobs_df["job_region"] == 'Санкт-Петербург')) & (~jobs_df["job_name"].isna())  & (jobs_df["job_name"] != "nan") ]

cnt = 0
for index_job, row_job in jobs_for_generations.iterrows():
  cnt_gen_job = 0
  print(f"index_job: {index_job}")
  candidates_for_generations = candidates_df[(~candidates_df["position"].isna()) & (candidates_df["position"] != "nan") & (candidates_df["job_id"]!= row_job["job_id"])].copy()
  for index_cand, row_cand in candidates_for_generations.sample(frac=0.7).iterrows():
    position = row_cand["position"]
    job_name = row_job["job_name"]
    prc_sim = tanimoto(str(position), str(job_name))
    prc_desc = tanimoto(str(row_cand["skills"]), str(row_job["job_description"]))
    if prc_sim == 0 or prc_sim > 0.3 or prc_desc > 0.5:
      continue 
    new_row = candidates_for_generations.loc[index_cand].copy()
    new_row["job_id"] = row_job["job_id"]
    new_row["candidate_status_id"] = 0
    new_row["status"] = "Negative row"
    local_df = local_df.append(new_row)
    cnt_gen_job+=1
    cnt+=1
    if cnt_gen_job > 100:
      break
  # if index_job > 10:
  #   break

candidates_df = pd.concat([candidates_df, local_df], axis=0, ignore_index=True)
candidates_mask = candidates_df.duplicated(subset=["id", "job_id"])
candidates_df = candidates_df.loc[~candidates_mask]
# print(f"candidates_df.shape {candidates_df.shape}")


candidates_df.to_csv("ext_data_candidates.csv", index=False, encoding="utf-8-sig", sep=";", header=False)
