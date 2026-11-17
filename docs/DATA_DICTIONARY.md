# Data Dictionary: SupeRR Selector Season 2 Dataset

**Dataset Version:** 2022–2026 IPL & T20I Competition Data Pack  
**Scope:** Ball-by-ball event data, match metadata, tournament structures, and player registrations  

---

## 1. Table: `competitions.csv`
**Grain:** One row per tournament / competition edition.  
**Total Rows:** 141  

| Column Name | Data Type | Nullable | Description & Domain | Analytical Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `comp_id` | Integer | No | Unique competition identifier (e.g. `1358`, `2193`). | Primary key. Joins with `matches`, `teams`, `competition_team_player_mapping`. |
| `comp_name` | String | No | Official competition title (e.g. "IPL 2024", "ICC Men's T20 World Cup", "India in England T20I Series 2022"). | Tournament identification and qualitative reporting. |
| `match_format`| String | No | Format of the competition: `'T20'` (franchise league) or `'T20I'` (international T20). | Competition tier stratification and baseline calibration. |
| `season` | String | No | Calendar season / year: `'2022'`, `'2022/23'`, `'2023'`, `'2023/24'`, `'2024'`, `'2024/25'`, `'2025'`, `'2026'`. | Temporal grouping and longitudinal trend analysis. |

---

## 2. Table: `matches.csv`
**Grain:** One row per scheduled match.  
**Total Rows:** 883  

| Column Name | Data Type | Nullable | Description & Domain | Analytical Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `match_id` | Integer | No | Unique match identifier (e.g. `13511`, `31281`). | Primary key. Relates to `ball_by_ball.csv` and `playing_eleven.csv`. |
| `comp_id` | Integer | No | Competition identifier. | Foreign key to `competitions.csv`. |
| `match_number`| Integer | Yes | Serial match sequence number within the competition. | Match sequencing. |
| `match_date` | Date | No | Date on which match took place (`YYYY-MM-DD`). | Chronological ordering and filtering. |
| `stage` | String | No | Tournament stage (`'League'`, `'Final'`, `'Qualifier'`, `'Eliminator'`, `'Semi Final'`, `'Super 4'`, `'Others'`). | Stakes weighting (knockouts carry elevated pressure). |
| `venue_id` | Integer | No | Numeric identifier for the host cricket ground. | Venue conditioning and home/away adjustments. |
| `venue_country`| String | No | Country where match occurred (17 nations: India, UAE, UK, NZ, etc.). | Regional pitch/climate context. |
| `home_team_id`| Integer | No | Team identifier for designated home/first team. | Team identification. |
| `home_team` | String | No | Team name for designated home/first team. | Reporting and human readability. |
| `away_team_id`| Integer | No | Team identifier for designated away/second team. | Team identification. |
| `away_team` | String | No | Team name for designated away/second team. | Reporting and human readability. |
| `home_team_captain_id` | Float | Yes | Player ID of home captain (44 nulls in abandoned/associate matches). | Leadership tracking. |
| `away_team_captain_id` | Float | Yes | Player ID of away captain (45 nulls). | Leadership tracking. |
| `toss_win_team_id` | Float | Yes | Team ID that won the coin toss (15 nulls in abandoned matches). | Tactical decision tracking. |
| `toss_opted` | String | Yes | Toss decision (`'bat'` or `'field'`). | Match strategy indicator. |
| `man_of_the_match` | String | Yes | Player named Player of the Match (or empty for abandoned). | Corroborating impact awards. |
| `first_inn_revised_overs` | Float | Yes | Revised overs for Innings 1 under rain interruptions / DLS. | Innings length normalization. |
| `second_inn_revised_overs`| Float | Yes | Revised overs for Innings 2 under rain interruptions / DLS. | Target calculation & balls remaining baseline. |
| `revised_target` | Float | Yes | Revised run target for 2nd innings under DLS method (23 matches). | **Crucial:** Sets chase target for rain-affected chases. |
| `knock_out` | Integer | No | Binary flag: `1` if playoff / knockout / elimination tie, `0` otherwise. | Contextual pressure amplifier. |
| `win_team_id` | Float | Yes | Team ID of match winner (NaN for No Result / Abandoned / Ties). | Match outcome verification. |
| `result` | String | No | Text description of result (e.g. "India Won by 7 wickets", "Match Abandoned"). | Match outcome verification. |

---

## 3. Table: `teams.csv`
**Grain:** One row per team per competition.  
**Total Rows:** 353  

| Column Name | Data Type | Nullable | Description & Domain | Analytical Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `comp_id` | Integer | No | Competition identifier. | Foreign key to `competitions.csv`. |
| `team_id` | Integer | No | Team identifier (38 unique teams). | Primary key within team table. |
| `team_name` | String | No | Official franchise or national team name. | Display and grouping. |

---

## 4. Table: `playing_eleven.csv`
**Grain:** One row per player in a match squad.  
**Total Rows:** 28,381  

| Column Name | Data Type | Nullable | Description & Domain | Analytical Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `match_id` | Integer | No | Match identifier. | Foreign key to `matches.csv`. |
| `team_id` | Integer | No | Team identifier. | Foreign key to `teams.csv`. |
| `player_id` | Integer | No | Unique player identifier. | Foreign key to player catalog. |
| `batting_order`| Float | Yes | Nominal batting line-up position assigned prior to match (`1` to `13`). | Pre-game role assignment. |
| `is_played` | Boolean | No | `True` if player took the field (playing XI or impact sub); `False` if bench squad. | Filtering active match participants. |
| `is_captain`| Boolean | Yes | `True` if player captained the team. | Role descriptor. |
| `is_wk` | Boolean | Yes | `True` if designated wicketkeeper. | Role descriptor. |
| `is_impact` | Integer | No | `1` if player entered match as tactical Impact Player substitute; `0` otherwise. | Impact player tracking (IPL 2023+). |
| `is_impact_off`| Integer| No | `1` if player was substituted off under Impact Player regulation; `0` otherwise. | Impact player substitution tracking. |

---

## 5. Table: `competition_team_player_mapping.csv`
**Grain:** One row per player registered for a team in a tournament.  
**Total Rows:** 6,413  

| Column Name | Data Type | Nullable | Description & Domain | Analytical Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `comp_id` | Integer | No | Competition identifier. | Tournament link. |
| `comp_name` | String | No | Competition title. | Human readability. |
| `team_id` | Integer | No | Team identifier. | Team link. |
| `team_name` | String | No | Team name. | Human readability. |
| `player_id` | Integer | No | Unique player identifier (1,217 players). | Universal player key across the entire project. |
| `player_name` | String | No | Player display name. | Reference label (Must be keyed by `player_id`). |

---

## 6. Table: `ball_by_ball.csv`
**Grain:** One row per delivery bowled.  
**Total Rows:** 200,999  

| Column Name | Data Type | Nullable | Description & Domain | Analytical Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `match_id` | Integer | No | Match identifier. | Relates to `matches.csv`. |
| `innings` | Integer | No | Innings number: `1` (1st Inn), `2` (2nd Inn), `3` (Super Over 1), `4` (Super Over 2). | Game state stratification. |
| `overid` | Integer | No | Over index in innings (`1` to `20`). 1-indexed. | Phase classification (Powerplay/Middle/Death). |
| `over_ball_num`| Integer| No | Ball count within over (`1` to `13`). | Over ball progression (including extras). |
| `innings_ball_num`| Integer| No | Monotonic delivery sequence within innings (`1` to `130+`). | Chronological sorting and cumulative aggregation. |
| `batting_team_id`| Integer| No | Team identifier of the batting team. | Team attribution. |
| `bowling_team_id`| Integer| No | Team identifier of the bowling team. | Team attribution. |
| `striker_id` | Integer | No | Unique player ID of batter facing delivery. | Batter performance attribution. |
| `striker_name`| String | No | Batter name. | Reference label. |
| `non_striker_id`| Integer| No | Unique player ID of non-striker. | Partnership tracking. |
| `non_striker_name`| String| No | Non-striker name. | Reference label. |
| `bowler_id` | Integer | No | Unique player ID of bowler delivering the ball. | Bowler performance attribution. |
| `bowler_name` | String | No | Bowler name. | Reference label. |
| `batting_type` | String | No | Batting stance: `'RHB'` (Right Hand Bat) or `'LHB'` (Left Hand Bat). | Matchup / platoon split analysis. |
| `bowling_type` | String | No | Bowling style (e.g. `'Right-arm Fast'`, `'Slow left-arm orthodox'`). | Bowler category analysis. |
| `batting_order`| Integer | No | Position in batting order for the striker (`1` to `13`). | Anchor vs finisher role context. |
| `runs` | Integer | No | Runs scored **off the bat** (`0, 1, 2, 3, 4, 5, 6`). | Batter run scoring calculation. |
| `is_four` | Boolean | No | `True` if delivery yielded a 4 off the bat; `False` otherwise. | Boundary percentage calculation. |
| `is_six` | Boolean | No | `True` if delivery yielded a 6 off the bat; `False` otherwise. | Maximum boundary calculation. |
| `is_wicket` | Boolean | No | `True` if a dismissal occurred on this delivery; `False` otherwise. | Wicket event identifier. |
| `dismissal_type_id` | Float | Yes | Numeric ID for dismissal mechanism (null for non-wickets). | Dismissal code. |
| `dismissal_type` | String | Yes | Type of dismissal (`'Caught'`, `'Bowled'`, `'LBW'`, `'RunOut'`, `'Stump'`, `'Hit Wicket'`, `'Retire Out'`, `'Obstructing the field'`). | Separates bowler wickets from fielding/runout dismissals. |
| `dismissed_player_id` | Float | Yes | Player ID of batter dismissed on this delivery. | Identifies which batter got out. |
| `extras_type` | String | Yes | Category of extras (`'wide'`, `'Overstep'`, `'legbyes'`, `'byes'`, `'other'`, `'Penalty'`, or `NaN`). | Governs legal delivery count and bowler penalty. |
| `extras1_runs` | Integer | No | Primary extra runs (wide runs, no-ball penalty, bye/legbye runs). | Extras run accounting. |
| `extras_2_runs` | Integer | No | Secondary extra runs (e.g., boundary byes off no-balls). | Extras run accounting. |
| `pace_or_spin` | String | No | Bowling discipline classification: `'Pace'` or `'Spin'`. | Tactical matchup analysis. |
| `bowl_speed` | Float | No | Recorded delivery speed in km/h (`-1.0` if unavailable). | Delivery pace attribute. |
| `stroke` | String | Yes | Shot played by batter (e.g. `'Pull shot'`, `'Cover Drive'`, `'Slog'`). | Batter strokeplay analysis. |
| `delivery_style` | String | Yes | Pitch movement / variation (`'Inswing'`, `'Off Cutter'`, `'Googly'`, `'Beamer'`). | Delivery variation classification. |
| `over_or_around` | String | Yes | Bowler trajectory relative to stumps: `'Over'` or `'Around'`. | Bowling angle analysis. |
| `on_or_off` | String | No | Pitch line / shot direction: `'Off-side'` or `'On-side'`. | Directional split. |
| `delivery_ist_time` | String | No | Delivery timestamp in IST. | Operational timestamp. |

---

## 7. Derivation Rules for Analytical Features

To guarantee 100% transparency and reproducibility, all derived metrics follow strict standardized mathematical definitions:

### 7.1 Delivery Validity and Ball Counting
1. **Legal Delivery (`is_legal`):**
   $$\text{is\_legal} = (\text{extras\_type} \notin \{\text{'wide'}, \text{'Overstep'}, \text{'other'}\})$$
2. **Batter Ball Faced (`is_ball_faced`):**
   $$\text{is\_ball\_faced} = (\text{extras\_type} \neq \text{'wide'})$$
   *(A batter faces legal balls and no-balls; wides do not count as a ball faced).*

### 7.2 Run Scoring and Extras Assignment
1. **Batter Runs (`bat_runs`):**
   $$\text{bat\_runs} = \text{runs}$$
2. **Total Delivery Runs (`total_runs`):**
   $$\text{total\_runs} = \text{runs} + \text{extras1\_runs} + \text{extras\_2\_runs}$$
3. **Bowler Runs Conceded (`bowler_runs`):**
   $$\text{bowler\_runs} = \text{runs} + \mathbb{I}(\text{extras\_type} \in \{\text{'wide'}, \text{'Overstep'}, \text{'other'}\}) \times \text{extras1\_runs}$$
   *(Byes, legbyes, and penalty runs are excluded from bowler statistics).*

### 7.3 Wicket Attribution
1. **Bowler Wicket (`is_bowler_wicket`):**
   $$\text{is\_bowler\_wicket} = \text{is\_wicket} \land (\text{dismissal\_type} \in \{\text{'Caught'}, \text{'Bowled'}, \text{'LBW'}, \text{'Stump'}, \text{'Hit Wicket'}\})$$
2. **Team Wicket Lost (`is_team_wicket`):**
   $$\text{is\_team\_wicket} = \text{is\_wicket} \lor (\text{dismissed\_player\_id is not null})$$

### 7.4 Pre-Delivery Game State Variables (Cumulative Before Ball)
For ball $t$ in a given match and innings:
1. **Cumulative Team Score Before Ball ($S_{t-1}$):**
   $$S_{t-1} = \sum_{k=1}^{t-1} \text{total\_runs}_k$$
2. **Cumulative Team Wickets Lost Before Ball ($W_{t-1}$):**
   $$W_{t-1} = \sum_{k=1}^{t-1} \text{is\_team\_wicket}_k$$
3. **Wickets in Hand ($W_{\text{hand}}$):**
   $$W_{\text{hand}} = 10 - W_{t-1}$$
4. **Legal Balls Consumed So Far ($B_{\text{bowled}}$):**
   $$B_{\text{bowled}} = \sum_{k=1}^{t-1} \text{is\_legal}_k$$
5. **Legal Balls Remaining in Innings ($B_{\text{rem}}$):**
   $$B_{\text{rem}} = \max\left(0, 120 - B_{\text{bowled}}\right) \quad (\text{adjusted if revised overs apply})$$
6. **Current Run Rate (CRR):**
   $$\text{CRR} = \begin{cases} \frac{S_{t-1} \times 6}{B_{\text{bowled}}}, & B_{\text{bowled}} > 0 \\ 0, & B_{\text{bowled}} = 0 \end{cases}$$

### 7.5 Second Innings Chase Metrics
1. **Target Score ($T$):**
   $$T = \begin{cases} \text{revised\_target}, & \text{if non-null in matches.csv} \\ S_{\text{inn1, total}} + 1, & \text{otherwise} \end{cases}$$
2. **Runs Needed Before Ball ($R_{\text{need}}$):**
   $$R_{\text{need}} = \max(0, T - S_{t-1})$$
3. **Required Run Rate (RRR):**
   $$\text{RRR} = \begin{cases} \frac{R_{\text{need}} \times 6}{B_{\text{rem}}}, & B_{\text{rem}} > 0 \\ R_{\text{need}} \times 6, & B_{\text{rem}} = 0 \end{cases}$$

---

## 8. Summary of Data Dictionary Standards

This dictionary establishes the formal contract for all subsequent data engineering, situational segmentation, expected run modeling, and player rating workflows.
