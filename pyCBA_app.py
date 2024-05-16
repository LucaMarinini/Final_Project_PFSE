import pycba as cba
import streamlit as st
import pandas as pd
#import forallpeople as si -> Future possible implementation

st.header("Eurocode/NTC18 preliminary bridge analysis")
st.write("Based on the library 'PyCBA' from Colin Caprani. For any other information refers to:")
st.link_button("PyCBA on GitHub", "https://github.com/ccaprani/pycba")
st.write("In this version it is up to the user to adopt consistent units e.g. kN, m, m^2, m^4, etc.")
st.sidebar.subheader("General Input")

# DEFINITION OF GEOMETRY
n_spans = st.sidebar.number_input("Number of spans []", value = 3,  step = 1)
spans_E = st.sidebar.number_input("Elastic modulus [kPa]",value= 35000000) #constant for all the spans

tab0, tab1, tab2, tab3 = st.tabs(["Description", "Beam configuration","Vehicle definition", "Analysis results"])

with tab0:
    st.write("This is a very useful software for preliminary analysis of bridge structures, based on the PyCBA library developed by Prof. Colin Caprani")
    st.markdown("""
                The app is divided in three different tabs:
                - Beam configuration: input data can be defined for beam geometry and for dead/permanent load configuration;
                - Vehicle definition: two vehicle type definition are possible. The first one is a pre-defined scheme representing the Load Model 1 of Eurocode, while the second one lets the user decide the configuration of vehicle. Both concentrated and distributed loads can be defined.
                - Analysis results: in this tab there isn't any input button. Instead, a run analysis button can be used by the user to obtain the analysis results in terms of bending moment, shear force and support reations, as a total envelope or in details for dead and live loads.
                """)
    st.divider()
    disclaimer = "THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
    st.markdown("""
    <style>
    .small-font {
    font-size:11px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown(f'<p class="small-font">{disclaimer}</p>', unsafe_allow_html=True)

with tab1:
    container_geometry = st.container(border=True)
    with container_geometry:
        cols_spans = st.columns(n_spans)
        span_lengths = []
        spans_EI = []
        supports = []
        element_types = []
        for count, span in enumerate(range(1, n_spans+1)):
            with cols_spans[count]:
                span_length = st.number_input(f"Lenght of span number {span} in m",  value=30.0)
                span_I = st.number_input(f"Inertia of section for span number {span} in m^4", value=2.0)
                EI = spans_E * span_I
                spans_EI.append(EI)
                n_supports = n_spans + 1
                span_lengths.append(span_length)

                element_types_checkbox = st.selectbox(f"Element type for span number {span}", 
                                            options = ("Fixed-Fixed", "Fixed-Pinned","Pinned-Fixed", "Pinned-Pinned"))
                if element_types_checkbox == "Fixed-Fixed":
                    element_type = 1
                elif element_types_checkbox == "Fixed-Pinned":
                    element_type = 2
                elif element_types_checkbox == "Pinned-Fixed":
                    element_type = 3
                elif element_types_checkbox == "Pinned-Pinned":
                    element_type = 4
                element_types.append(element_type)
        cols_supports = st.columns(n_supports)
        for count,support in enumerate(range(1, n_supports+1)):
            with cols_supports[count]:
                supports_type_checkbox = st.selectbox(f"Restraint for support number {support}", options = ("Fixed", "Hinged","Free"))
                if supports_type_checkbox == "Fixed":
                    x = -1
                    y = -1
                elif supports_type_checkbox == "Hinged":
                    x = -1
                    y = 0
                elif supports_type_checkbox == "Free":
                    x = 0
                    y = 0
                supports.append(x)
                supports.append(y)

    container_loads = st.container(border=True)
    with container_loads:
        dead_loads = []
        perm_loads = []
        cols_loads = st.columns(n_spans)
        for count, span in enumerate(range(1, n_spans+1)):
            with cols_loads[count]:
                deadload = st.number_input(f"Dead load for span number {span} in kN/m",  value=10.0)
                dead_loads.append(deadload)
                permload = st.number_input(f"Permanent load for span number {span} in kN/m", value=10.0)
                perm_loads.append(permload)
        cols_gamma_g, cols_gamma_p = st.columns(2)

        with cols_gamma_g:
            gamma_g = st.number_input(f"Partial load factor for dead loads", value=1.0)
        with cols_gamma_p:
            gamma_p = st.number_input(f"Partial load factor for permanent loads", value=1.0)

# DEFINITION OF VEHICLE
with tab2:
    cw_width = st.number_input("Carriageway width in m", value=10.0)
    n_lanes = int(cw_width / 3)

    vehicle_type = st.selectbox(f"Type of vehicle", options= ("Eurocode", "User defined"))
       
    if vehicle_type == "Eurocode":
        lm1_lane1_dist = 27 #kN/m
        lm1_lane2_dist = 7.5 #kN/m
        lm1_lane3_dist = 7.5 #kN/m
        lm1_remaining = 2.5 #kN/m^2

        lm1_lane1_conc = 300 #load for axle in kN
        lm1_lane2_conc = 200 #load for axle in kN
        lm1_lane3_conc = 100 #load for axle in kN

        lm1_spacing = [1.2] #m

        if n_lanes < 1:
            raise ValueError("Carriageway width is too tight to allow vehicle passage. Please define a carriageway width > 3.00m")
        elif n_lanes >= 1 and n_lanes < 2:
            lm1_dist = lm1_lane1_dist + lm1_remaining * (cw_width - 3 * n_lanes)
            lm1_conc = lm1_lane1_conc
        elif n_lanes >= 2 and n_lanes < 3:
            lm1_dist = lm1_lane1_dist + lm1_lane2_dist + lm1_remaining * (cw_width - 3 * n_lanes)
            lm1_conc = lm1_lane1_conc + lm1_lane2_conc
        elif n_lanes >= 3:
            lm1_dist = lm1_lane1_dist + lm1_lane2_dist + lm1_lane3_dist + lm1_remaining * (cw_width - 9)
            lm1_conc = lm1_lane1_conc + lm1_lane2_conc + lm1_lane3_conc

        vehicle_dist = lm1_dist
        vehicle_conc = [lm1_conc, lm1_conc]
        vehicle_spacing = lm1_spacing

        st.write(f"Max number of full lane on the carriageway is: {n_lanes}")
        st.write(f"The max distributed load, obtained as the sum of all the lanes and (potential) remaining area is: {lm1_dist} kN/m")
        st.write(f"The max concentrated load, obtained as the sum of all the front (or rear) axle is: {lm1_conc} kN")
        st.write(f"The axle spacing of Eurocode LM1 vehicle is: {lm1_spacing[0]} m")

    elif vehicle_type == "User defined":
        #Insert user defined vehicle
        vehicle_n_axis = st.number_input("Number of vehicle axis", value = 2,  step = 1)
        vehicle_n_spacing = vehicle_n_axis - 1
        vehicle_conc = []
        vehicle_spacing = []
        cols_vehicle_axis = st.columns(vehicle_n_axis)
        for count, axle in enumerate(range(1, vehicle_n_axis+1)):
            with cols_vehicle_axis[count]:    
                axle_weight = st.number_input(f"Weight in kN for axle {axle}",  value=100.0)
            vehicle_conc.append(axle_weight)
        cols_vehicle_spacing = st.columns(vehicle_n_spacing)
        for count, spacing in enumerate(range(1, vehicle_n_spacing+1)):
            with cols_vehicle_spacing[count]:    
                axle_spacing = st.number_input(f"Spacing between axle {spacing}-{spacing+1} in m",  value=1.00)
            vehicle_spacing.append(axle_spacing)

        cols_vehicle_dist_1, cols_vehicle_dist_2 = st.columns(2)
        with cols_vehicle_dist_1:
            vehicle_dist_checkbox = st.checkbox("Distributed load")
        if vehicle_dist_checkbox == True:
            with cols_vehicle_dist_2:
                vehicle_dist_distributed = st.number_input(f"Distributed load for user defined vehicle, in kN/m^2")
                vehicle_dist = vehicle_dist_distributed * cw_width
        else:
            vehicle_dist = 0

    gamma_q_max = st.number_input("Partial load factor for vehicle load", value=1.0)
    gamma_q_min = 0

with tab3:
    # CREATE BEAM MODEL, DESIGN VEHICLE AND BRIDGE ANALYSIS
    run_button = st.button('Run analysis')
    if run_button == True:
        LMg = []
        LMp = []
        LMq = []
        for count, span in enumerate(range(1, n_spans+1)):
            LMg_single_span = [span, 1, dead_loads[count] , 0, 0]
            LMg.append(LMg_single_span)
        for count, span in enumerate(range(1, n_spans+1)):
            LMp_single_span = [span, 1, perm_loads[count] , 0, 0]
            LMp.append(LMp_single_span)
        for span in range(1, n_spans+1):
            LMq_single_span = [span, 1, vehicle_dist, 0, 0]
            LMq.append(LMq_single_span)

        # Evaluate load factors and create the loadpattern for static analysis
        gamma_g_max = gamma_g
        gamma_g_min = 1.0
        gamma_p_max = gamma_p
        gamma_p_min = 1.0

        # Combine the dead and permanent loads in a single load matrix
        LMd=[]
        for count, load in enumerate(LMg):
            sum_load = LMg[count][2] * gamma_g_max + LMp[count][2] * gamma_p_max
            span_vector = [LMg[count][0], LMg[count][1], sum_load, LMg[count][3], LMg[count][4]]
            LMd.append(span_vector)
        gamma_d_max = 1.0
        gamma_d_min = 1.0

        # Create the load pattern for envelope of UDL
        bridge = cba.BeamAnalysis(L=span_lengths, EI=spans_EI,R=supports, eletype=element_types) # A beam analysis with just geometry configuration
        
        load_pattern = cba.LoadPattern(bridge)
        load_pattern.set_dead_loads(LMd,gamma_d_max, gamma_d_min)
        load_pattern.set_live_loads(LMq,gamma_q_max, gamma_q_min)
        env_udl = load_pattern.analyze()

        # Create bridge analysis with run vehicle
        vehicle_conc_fact = []
        for conc in vehicle_conc:
            factored = conc * gamma_q_max
            vehicle_conc_fact.append(factored)
        vehicle = cba.Vehicle(axle_spacings=vehicle_spacing, axle_weights=vehicle_conc_fact)
        bridge_analysis = cba.BridgeAnalysis(ba=bridge, veh=vehicle)
        env_veh = bridge_analysis.run_vehicle(step=0.5)
        mmax_veh = env_veh.Mmax
        mmin_veh = env_veh.Mmin
        vmax_veh = env_veh.Vmax
        vmin_veh = env_veh.Vmin

        # Create the load pattern with envelope of envelopes (augment method)
        envenv = cba.Envelopes.zero_like(env_udl)
        envenv.augment(env_udl)
        envenv.augment(env_veh)

    # OUTPUT OF BRIDGE ANALYSIS
        plot = envenv.plot()[0] #bending moment and shear force
        st.pyplot(plot)

    # TEST ADDITIONAL OUTPUT
        # Results for single span
        x_axis = envenv.x
        mmax = envenv.Mmax
        mmin = envenv.Mmin
        vmax = envenv.Vmax
        vmin = envenv.Vmin
        span_coord = [0]
        for count, length in enumerate(span_lengths, start=1):
            span_coord_previous = span_coord[count-1]
            delta_length = span_lengths[count-1]           
            span_coord_i = span_coord_previous + delta_length
            span_coord.append(span_coord_i)

        for count, span in enumerate(range(1, n_spans+1)):
            span_coord_min =  span_coord[count]
            span_coord_max = span_coord[count+1]
            span_M_max = mmax[(span_coord_min <= x_axis) & (x_axis <=span_coord_max)]
            span_M_min = mmin[(span_coord_min <= x_axis) & (x_axis <=span_coord_max)]
            st.write(f"Bending moment in span number {count+1}: Max={round(span_M_max.max(),2)} kNm | Min = {round(span_M_min.min(),2)} kNm")

        for count, span in enumerate(range(1, n_spans+1)):
            span_coord_min =  span_coord[count]
            span_coord_max = span_coord[count+1]
            span_V_max = vmax[(span_coord_min <= x_axis) & (x_axis <=span_coord_max)]
            span_V_min = vmin[(span_coord_min <= x_axis) & (x_axis <=span_coord_max)]
            st.write(f"Shear force in span number {count+1}: Max={round(span_V_max.max(),2)} kN | Min = {round(span_V_min.min(),2)} kN")

    #Results for single load case
        criticals = bridge_analysis.critical_values(envenv)
        # st.write(criticals)

        load_cases = {"DEAD": LMg, "PERM": LMp, "LIVE": LMq}
        results_acc = {}
        for load_case_name, load_matrix in load_cases.items():
            beam_model = cba.BeamAnalysis(L=span_lengths, EI=spans_EI,R=supports, eletype=element_types, LM=load_matrix)
            beam_model.analyze()
            results_acc[load_case_name] = {} # nested accumulator to store each kind of result
            results_acc[load_case_name].update({'shear': beam_model.beam_results.results.V})
            results_acc[load_case_name].update({'moment': beam_model.beam_results.results.M})
            results_acc[load_case_name].update({'deflection': beam_model.beam_results.results.D})
            results_acc[load_case_name].update({'reactions': beam_model.beam_results.R})

        shear_dead = results_acc["DEAD"]["shear"]
        shear_perm = results_acc["PERM"]["shear"]
        shear_live = results_acc["LIVE"]["shear"]
        mom_dead = results_acc["DEAD"]["moment"]
        mom_perm = results_acc["PERM"]["moment"]
        mom_live = results_acc["LIVE"]["moment"]

        # st.table(shear_dead)
        df_col = ["Bridge_x [m]", "Shear_dead [kN]","Shear_perm [kN]", "Shear_live [kN]", "Shear_veh_max [kN]", "Shear_veh_min [kN]"]
        df_res=list(zip(envenv.x, shear_dead, shear_perm, shear_live, vmax_veh, vmin_veh))
        df =pd.DataFrame(df_res, columns=df_col)

        df_colm = ["Bridge_x [m]", "Moment_dead [kNm]", "Moment_perm [kNm]", "Moment_live [kNm]", "Moment_veh_max [kNm]", "Moment_veh_min [kNm]"]
        df_resm=list(zip(envenv.x, mom_dead, mom_perm, mom_live, mmax_veh, mmin_veh))
        dfm=pd.DataFrame(df_resm, columns=df_colm)

        st.divider()
        st.markdown("""
                    Detailed numerical data
                    """)
        st.table(df)
        st.table(dfm)
        