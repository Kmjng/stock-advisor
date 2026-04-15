import ctypes

WM_USER = 0x0400
CA_WMCAEVENT = WM_USER + 8400
CA_CONNECTED = WM_USER + 110
CA_DISCONNECTED = WM_USER + 120
CA_SOCKETERROR = WM_USER + 130
CA_RECEIVEDATA = WM_USER + 210
CA_RECEIVESISE = WM_USER + 220
CA_RECEIVEMESSAGE = WM_USER + 230
CA_RECEIVECOMPLETE = WM_USER + 240
CA_RECEIVEERROR = WM_USER + 250


# --- Login structures ---

class ACCOUNTINFO(ctypes.Structure):
    _fields_ = [
        ("szAccountNo", ctypes.c_char * 11),
        ("szAccountName", ctypes.c_char * 40),
        ("act_pdt_cdz3", ctypes.c_char * 3),
        ("amn_tab_cdz4", ctypes.c_char * 4),
        ("expr_datez8", ctypes.c_char * 8),
        ("granted", ctypes.c_char * 1),
        ("filler", ctypes.c_char * 189),
    ]

class LOGININFO(ctypes.Structure):
    _fields_ = [
        ("szDate", ctypes.c_char * 14),
        ("szServerName", ctypes.c_char * 15),
        ("szUserID", ctypes.c_char * 8),
        ("szAccountCount", ctypes.c_char * 3),
        ("accountlist", ACCOUNTINFO * 999),
    ]

class LOGINBLOCK(ctypes.Structure):
    _fields_ = [
        ("TrIndex", ctypes.c_int),
        ("pLoginInfo", ctypes.POINTER(LOGININFO)),
    ]

class MSGHEADER(ctypes.Structure):
    _fields_ = [
        ("msg_cd", ctypes.c_char * 5),
        ("user_msg", ctypes.c_char * 80),
    ]

class RECEIVED(ctypes.Structure):
    _fields_ = [
        ("szBlockName", ctypes.c_char_p),
        ("szData", ctypes.c_void_p),
        ("nLen", ctypes.c_int),
    ]

class OUTDATABLOCK(ctypes.Structure):
    _fields_ = [
        ("TrIndex", ctypes.c_int),
        ("pData", ctypes.POINTER(RECEIVED)),
    ]


# --- C8201: Account holdings ---
# Each field: char name[N]; char _name;  (separator = 1 byte)

class Tc8201InBlock(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("pswd_noz8", ctypes.c_char * 44), ("_pswd_noz8", ctypes.c_char * 1),
        ("bnc_bse_cdz1", ctypes.c_char * 1), ("_bnc_bse_cdz1", ctypes.c_char * 1),
        ("aet_bsez1", ctypes.c_char * 1), ("_aet_bsez1", ctypes.c_char * 1),
        ("qut_dit_cdz3", ctypes.c_char * 3), ("_qut_dit_cdz3", ctypes.c_char * 1),
    ]  # 44+1+1+1+1+1+3+1 = 53

class Tc8201OutBlock(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("dpsit_amtz16", ctypes.c_char * 16), ("_dpsit_amtz16", ctypes.c_char * 1),
        ("mrgn_amtz16", ctypes.c_char * 16), ("_mrgn_amtz16", ctypes.c_char * 1),
        ("mgint_npaid_amtz16", ctypes.c_char * 16), ("_mgint_npaid_amtz16", ctypes.c_char * 1),
        ("chgm_pos_amtz16", ctypes.c_char * 16), ("_chgm_pos_amtz16", ctypes.c_char * 1),
        ("cash_mrgn_amtz16", ctypes.c_char * 16), ("_cash_mrgn_amtz16", ctypes.c_char * 1),
        ("subst_mgamt_amtz16", ctypes.c_char * 16), ("_subst_mgamt_amtz16", ctypes.c_char * 1),
        ("coltr_ratez6", ctypes.c_char * 6), ("_coltr_ratez6", ctypes.c_char * 1),
        ("rcble_amtz16", ctypes.c_char * 16), ("_rcble_amtz16", ctypes.c_char * 1),
        ("order_pos_csamtz16", ctypes.c_char * 16), ("_order_pos_csamtz16", ctypes.c_char * 1),
        ("ecn_pos_csamtz16", ctypes.c_char * 16), ("_ecn_pos_csamtz16", ctypes.c_char * 1),
        ("nordm_loan_amtz16", ctypes.c_char * 16), ("_nordm_loan_amtz16", ctypes.c_char * 1),
        ("etc_lend_amtz16", ctypes.c_char * 16), ("_etc_lend_amtz16", ctypes.c_char * 1),
        ("subst_amtz16", ctypes.c_char * 16), ("_subst_amtz16", ctypes.c_char * 1),
        ("sln_sale_amtz16", ctypes.c_char * 16), ("_sln_sale_amtz16", ctypes.c_char * 1),
        ("bal_buy_ttamtz16", ctypes.c_char * 16), ("_bal_buy_ttamtz16", ctypes.c_char * 1),
        ("bal_ass_ttamtz16", ctypes.c_char * 16), ("_bal_ass_ttamtz16", ctypes.c_char * 1),
        ("asset_tot_amtz16", ctypes.c_char * 16), ("_asset_tot_amtz16", ctypes.c_char * 1),
        ("actvt_type10", ctypes.c_char * 10), ("_actvt_type10", ctypes.c_char * 1),
        ("lend_amtz16", ctypes.c_char * 16), ("_lend_amtz16", ctypes.c_char * 1),
        ("accnt_mgamt_ratez6", ctypes.c_char * 6), ("_accnt_mgamt_ratez6", ctypes.c_char * 1),
        ("sl_mrgn_amtz16", ctypes.c_char * 16), ("_sl_mrgn_amtz16", ctypes.c_char * 1),
        ("pos_csamt1z16", ctypes.c_char * 16), ("_pos_csamt1z16", ctypes.c_char * 1),
        ("pos_csamt2z16", ctypes.c_char * 16), ("_pos_csamt2z16", ctypes.c_char * 1),
        ("pos_csamt3z16", ctypes.c_char * 16), ("_pos_csamt3z16", ctypes.c_char * 1),
        ("pos_csamt4z16", ctypes.c_char * 16), ("_pos_csamt4z16", ctypes.c_char * 1),
        ("dpsit_amtz_d1_16", ctypes.c_char * 16), ("_dpsit_amtz_d1_16", ctypes.c_char * 1),
        ("dpsit_amtz_d2_16", ctypes.c_char * 16), ("_dpsit_amtz_d2_16", ctypes.c_char * 1),
        ("noticez30", ctypes.c_char * 30), ("_noticez30", ctypes.c_char * 1),
        ("tot_eal_plsz18", ctypes.c_char * 18), ("_tot_eal_plsz18", ctypes.c_char * 1),
        ("pft_rtz15", ctypes.c_char * 15), ("_pft_rtz15", ctypes.c_char * 1),
        ("nas_tot_amtz18", ctypes.c_char * 18), ("_nas_tot_amtz18", ctypes.c_char * 1),
        ("nas_tot_txtz8", ctypes.c_char * 8), ("_nas_tot_txtz8", ctypes.c_char * 1),
    ]  # 16*24 + 6*2 + 10 + 30 + 18*2 + 15 + 8 + 31 separators = 527

class Tc8201OutBlock1(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("issue_codez6", ctypes.c_char * 6), ("_issue_codez6", ctypes.c_char * 1),
        ("issue_namez40", ctypes.c_char * 40), ("_issue_namez40", ctypes.c_char * 1),
        ("bal_typez6", ctypes.c_char * 6), ("_bal_typez6", ctypes.c_char * 1),
        ("loan_datez10", ctypes.c_char * 10), ("_loan_datez10", ctypes.c_char * 1),
        ("bal_qtyz16", ctypes.c_char * 16), ("_bal_qtyz16", ctypes.c_char * 1),
        ("unstl_qtyz16", ctypes.c_char * 16), ("_unstl_qtyz16", ctypes.c_char * 1),
        ("slby_amtz16", ctypes.c_char * 16), ("_slby_amtz16", ctypes.c_char * 1),
        ("prsnt_pricez16", ctypes.c_char * 16), ("_prsnt_pricez16", ctypes.c_char * 1),
        ("lsnpf_amtz16", ctypes.c_char * 16), ("_lsnpf_amtz16", ctypes.c_char * 1),
        ("earn_ratez9", ctypes.c_char * 9), ("_earn_ratez9", ctypes.c_char * 1),
        ("mrgn_codez4", ctypes.c_char * 4), ("_mrgn_codez4", ctypes.c_char * 1),
        ("jan_qtyz16", ctypes.c_char * 16), ("_jan_qtyz16", ctypes.c_char * 1),
        ("expr_datez10", ctypes.c_char * 10), ("_expr_datez10", ctypes.c_char * 1),
        ("ass_amtz16", ctypes.c_char * 16), ("_ass_amtz16", ctypes.c_char * 1),
        ("issue_mgamt_ratez6", ctypes.c_char * 6), ("_issue_mgamt_ratez6", ctypes.c_char * 1),
        ("medo_slby_amtz16", ctypes.c_char * 16), ("_medo_slby_amtz16", ctypes.c_char * 1),
        ("post_lsnpf_amtz16", ctypes.c_char * 16), ("_post_lsnpf_amtz16", ctypes.c_char * 1),
    ]  # 6+40+6+10+16*8+9+4+16*2+10+6+16*2 + 17 seps = 252


# --- S8180: Order/execution history ---

class Ts8180InBlock(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("inq_gubunz1", ctypes.c_char * 1), ("_inq_gubunz1", ctypes.c_char * 1),
        ("pswd_noz8", ctypes.c_char * 44), ("_pswd_noz8", ctypes.c_char * 1),
        ("group_noz4", ctypes.c_char * 4), ("_group_noz4", ctypes.c_char * 1),
        ("mkt_slctz1", ctypes.c_char * 1), ("_mkt_slctz1", ctypes.c_char * 1),
        ("order_datez8", ctypes.c_char * 8), ("_order_datez8", ctypes.c_char * 1),
        ("issue_codez12", ctypes.c_char * 12), ("_issue_codez12", ctypes.c_char * 1),
        ("comm_order_typez2", ctypes.c_char * 2), ("_comm_order_typez2", ctypes.c_char * 1),
        ("conc_gubunz1", ctypes.c_char * 1), ("_conc_gubunz1", ctypes.c_char * 1),
        ("inq_seq_gubunz1", ctypes.c_char * 1), ("_inq_seq_gubunz1", ctypes.c_char * 1),
        ("sort_gubunz1", ctypes.c_char * 1), ("_sort_gubunz1", ctypes.c_char * 1),
        ("sell_buy_typez1", ctypes.c_char * 1), ("_sell_buy_typez1", ctypes.c_char * 1),
        ("mrgn_typez1", ctypes.c_char * 1), ("_mrgn_typez1", ctypes.c_char * 1),
        ("accnt_admin_typez1", ctypes.c_char * 1), ("_accnt_admin_typez1", ctypes.c_char * 1),
        ("order_noz10", ctypes.c_char * 10), ("_order_noz10", ctypes.c_char * 1),
        ("ctsz56", ctypes.c_char * 56), ("_ctsz56", ctypes.c_char * 1),
        ("trad_pswd1z8", ctypes.c_char * 44), ("_trad_pswd1z8", ctypes.c_char * 1),
        ("trad_pswd2z8", ctypes.c_char * 44), ("_trad_pswd2z8", ctypes.c_char * 1),
        ("IsPageUp", ctypes.c_char * 1), ("_IsPageUp", ctypes.c_char * 1),
    ]  # 1+44+4+1+8+12+2+1+1+1+1+1+1+10+56+44+44+1 + 18 seps = 251

class Ts8180OutBlock(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("emp_kor_namez20", ctypes.c_char * 20), ("_emp_kor_namez20", ctypes.c_char * 1),
        ("brch_namez30", ctypes.c_char * 30), ("_brch_namez30", ctypes.c_char * 1),
        ("buy_conc_qtyz14", ctypes.c_char * 14), ("_buy_conc_qtyz14", ctypes.c_char * 1),
        ("buy_conc_amtz19", ctypes.c_char * 19), ("_buy_conc_amtz19", ctypes.c_char * 1),
        ("sell_conc_qtyz14", ctypes.c_char * 14), ("_sell_conc_qtyz14", ctypes.c_char * 1),
        ("sell_conc_amtz19", ctypes.c_char * 19), ("_sell_conc_amtz19", ctypes.c_char * 1),
    ]  # 20+30+14+19+14+19 + 6 seps = 122

class Ts8180OutBlock1(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("order_datez8", ctypes.c_char * 8), ("_order_datez8", ctypes.c_char * 1),
        ("order_noz10", ctypes.c_char * 10), ("_order_noz10", ctypes.c_char * 1),
        ("orgnl_order_noz10", ctypes.c_char * 10), ("_orgnl_order_noz10", ctypes.c_char * 1),
        ("accnt_noz11", ctypes.c_char * 11), ("_accnt_noz11", ctypes.c_char * 1),
        ("accnt_namez20", ctypes.c_char * 20), ("_accnt_namez20", ctypes.c_char * 1),
        ("order_kindz20", ctypes.c_char * 20), ("_order_kindz20", ctypes.c_char * 1),
        ("trd_gubun_noz1", ctypes.c_char * 1), ("_trd_gubun_noz1", ctypes.c_char * 1),
        ("trd_gubunz20", ctypes.c_char * 20), ("_trd_gubunz20", ctypes.c_char * 1),
        ("trade_type_noz1", ctypes.c_char * 1), ("_trade_type_noz1", ctypes.c_char * 1),
        ("trade_type1z20", ctypes.c_char * 20), ("_trade_type1z20", ctypes.c_char * 1),
        ("issue_codez12", ctypes.c_char * 12), ("_issue_codez12", ctypes.c_char * 1),
        ("issue_namez40", ctypes.c_char * 40), ("_issue_namez40", ctypes.c_char * 1),
        ("order_qtyz10", ctypes.c_char * 10), ("_order_qtyz10", ctypes.c_char * 1),
        ("conc_qtyz10", ctypes.c_char * 10), ("_conc_qtyz10", ctypes.c_char * 1),
        ("order_unit_pricez12", ctypes.c_char * 12), ("_order_unit_pricez12", ctypes.c_char * 1),
        ("conc_unit_pricez12", ctypes.c_char * 12), ("_conc_unit_pricez12", ctypes.c_char * 1),
        ("crctn_canc_qtyz10", ctypes.c_char * 10), ("_crctn_canc_qtyz10", ctypes.c_char * 1),
        ("cfirm_qtyz10", ctypes.c_char * 10), ("_cfirm_qtyz10", ctypes.c_char * 1),
        ("media_namez12", ctypes.c_char * 12), ("_media_namez12", ctypes.c_char * 1),
        ("proc_emp_noz5", ctypes.c_char * 5), ("_proc_emp_noz5", ctypes.c_char * 1),
        ("proc_timez8", ctypes.c_char * 8), ("_proc_timez8", ctypes.c_char * 1),
        ("proc_termz8", ctypes.c_char * 8), ("_proc_termz8", ctypes.c_char * 1),
        ("proc_typez12", ctypes.c_char * 12), ("_proc_typez12", ctypes.c_char * 1),
        ("rejec_codez5", ctypes.c_char * 5), ("_rejec_codez5", ctypes.c_char * 1),
        ("avail_qtyz10", ctypes.c_char * 10), ("_avail_qtyz10", ctypes.c_char * 1),
        ("mkt_typez1", ctypes.c_char * 1), ("_mkt_typez1", ctypes.c_char * 1),
        ("shsll_typez20", ctypes.c_char * 20), ("_shsll_typez20", ctypes.c_char * 1),
        ("passwd_noz8", ctypes.c_char * 8), ("_passwd_noz8", ctypes.c_char * 1),
        ("anw_cld_mkt_orr_no1z10", ctypes.c_char * 10), ("_anw_cld_mkt_orr_no1z10", ctypes.c_char * 1),
        ("anw_cld_mkt_orr_no2z10", ctypes.c_char * 10), ("_anw_cld_mkt_orr_no2z10", ctypes.c_char * 1),
        ("sor_mkt_orr_noz10", ctypes.c_char * 10), ("_sor_mkt_orr_noz10", ctypes.c_char * 1),
        ("rmt_mkt_cdz3", ctypes.c_char * 3), ("_rmt_mkt_cdz3", ctypes.c_char * 1),
        ("snd_mkt_cdz3", ctypes.c_char * 3), ("_snd_mkt_cdz3", ctypes.c_char * 1),
        ("sor_mkt_sli_ynz1", ctypes.c_char * 1), ("_sor_mkt_sli_ynz1", ctypes.c_char * 1),
        ("sop_cnd_prz15", ctypes.c_char * 15), ("_sop_cnd_prz15", ctypes.c_char * 1),
        ("rjt_qtyz18", ctypes.c_char * 18), ("_rjt_qtyz18", ctypes.c_char * 1),
        ("rmt_mkt_nmz50", ctypes.c_char * 50), ("_rmt_mkt_nmz50", ctypes.c_char * 1),
        ("sop_cnd_pr_rch_ynz1", ctypes.c_char * 1), ("_sop_cnd_pr_rch_ynz1", ctypes.c_char * 1),
        ("can_qtyz18", ctypes.c_char * 18), ("_can_qtyz18", ctypes.c_char * 1),
    ]  # 504

class Ts8180OutBlock_IN(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("ctsz56", ctypes.c_char * 56), ("_ctsz56", ctypes.c_char * 1),
        ("nextbutton", ctypes.c_char * 1), ("_nextbutton", ctypes.c_char * 1),
    ]  # 59


# --- Helper functions ---

def init_block(block):
    ctypes.memset(ctypes.addressof(block), 0x20, ctypes.sizeof(block))

def parse_field(raw_bytes, encoding="ascii"):
    if isinstance(raw_bytes, bytes):
        try:
            return raw_bytes.decode(encoding).strip()
        except (UnicodeDecodeError, AttributeError):
            return raw_bytes.strip().decode(encoding, errors="replace")
    return str(raw_bytes).strip()

def parse_int(raw_bytes):
    s = parse_field(raw_bytes, "ascii")
    try:
        return int(s)
    except (ValueError, TypeError):
        return 0

def parse_float(raw_bytes):
    s = parse_field(raw_bytes, "ascii")
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0
