# --- World Lore Summaries ---
world_lore_summaries = {
    "dark_fantasy": "Bu dünya, yıkılmış krallıkların, lanetli varlıkların ve gölgelerde gizlenen tehlikelerin hüküm sürdüğü karanlık bir fantezi diyarıdır. Hayatta kalmak zordur ve güven nadir bulunur. Kül Lejyonu (ölümsüz savaşçılar), Gölge Sendikası (kurnaz casuslar) ve Kadim Kült (kaotik varlıklara tapanlar) ana güçlerdir.",
    "animal_kingdom": "Bu dünya, bilinç kazanmış hayvan ırklarının yaşadığı, doğa ile iç içe bir krallıktır. Vargar (kurtlar), Vulpex (tilkiler), Noctis (baykuşlar) ve Leporim (tavşanlar) gibi ırklar kendi toplumlarını kurmuşlardır. Politika, kurnazlık ve hayatta kalma mücadelesi ön plandadır. Büyük Meşe Konseyi önemli bir toplanma yeridir."
}

# --- Initial Scenarios (Generic - Now Deprecated for specific starts) ---
initial_scenario_dark_fantasy = {
    "world_name_display": "Karanlık Fantezi Dünyası",
    "world_id": "dark_fantasy",
    "text": "Kara sislerin sardığı lanetli krallıkta, çatlamış bir yol ayrımındasın. Solunda, kemiklerle dolu bir çukur; sağında, kırık zincirlerinden sıyrılmış bir 'Yarı-Ölü' seni işaret parmağıyla çağırıyor. Arkanda ise homurdanan bir Canavarlar sürüsü yaklaşıyor. Ne yaparsın?",
    "choices": [
        {"id": "A", "text": "Yarı-Ölü'nün peşinden git."},
        {"id": "B", "text": "Kemik çukuruna atla."},
        {"id": "C", "text": "Canavarlarla savaşmayı göze al."}
    ],
    "current_location_id": "df_crossroads_01"
}

initial_scenario_animal_kingdom = {
    "world_name_display": "Hayvanların Hüküm Sürdüğü Dünya",
    "world_id": "animal_kingdom",
    "text": "Güneşin altın ışıklarıyla yıkanan devasa bir ağacın kovuğunda gözlerini açıyorsun. Etrafın, konuşan sincapların ve şarkı söyleyen kuşların neşeli sesleriyle dolu. Aşağıda, farklı hayvan klanlarının temsilcilerinin toplandığı bir meclis alanı görünüyor. Anlaşılan o ki, 'Büyük Meşe Konseyi' başlamak üzere. Ne yaparsın?",
    "choices": [
        {"id": "A", "text": "Konsey alanına doğru dikkatlice in."},
        {"id": "B", "text": "Etraftaki diğer hayvanlarla konuşarak bilgi topla."},
        {"id": "C", "text": "Ağacın daha yükseklerine tırmanarak etrafı gözlemle."}
    ],
    "current_location_id": "ak_great_oak_01"
}

# Dictionary to hold all initial scenarios (used as fallback or if no race/faction selected)
initial_scenarios_by_world = {
    "dark_fantasy": initial_scenario_dark_fantasy,
    "animal_kingdom": initial_scenario_animal_kingdom
}

# --- Race/Faction Specific Starting Scenarios ---
starting_scenarios = {
    "animal_kingdom": {
        "vargar": {
            "text": "Sürünün av borusu yankılanıyor. Lideriniz Tharok, bu geceki avın hedefinin yakındaki Leporim tarlalarına sızan gizemli bir yaratık olduğunu söylüyor. Ay ışığı altında keskinleşen duyularınla ormanın kenarında bekliyorsun. Ne yaparsın?",
            "choices": [
                {"id": "A", "text": "Doğrudan yaratığın izini sürmeye başla."},
                {"id": "B", "text": "Sürüdeki diğer tecrübeli avcılarla konuşup plan yap."},
                {"id": "C", "text": "Rüzgarı koklayarak ve etrafı dinleyerek daha fazla bilgi topla."}
            ],
            "current_location_id": "ak_vargar_start_forest_edge"
        },
        "vulpex": {
            "text": "Kıvılcım Loncası'nın gizli atölyesinde, yeni 'Buhar Kapanı'nın son parçalarını birleştiriyorsun. Dışarıdan Vargar devriyelerinin ulumaları geliyor. Kapanı test etmek için mükemmel bir fırsat mı, yoksa fazla mı riskli? Ne yaparsın?",
            "choices": [
                {"id": "A", "text": "Kapanı alıp yakındaki bir geçide kur."},
                {"id": "B", "text": "Atölyede kalıp kapanın mekanizmasını daha da geliştir."},
                {"id": "C", "text": "Gizlice dışarı sızıp Vargar devriyesinin hareketlerini gözlemle."}
            ],
             "current_location_id": "ak_vulpex_start_workshop"
        },
        "noctis": {
            "text": "Uçan Kule Tapınağı'ndaki gözlem odanda, yıldız haritası önünde duruyor. 'Kanla Yazılmış Barış' kehanetinin yeni bir yorumu zihninde beliriyor - bu bir barış değil, yaklaşan bir savaşın gölgesi olabilir. Bu bilgiyi kiminle paylaşmalısın? Ne yaparsın?",
            "choices": [
                {"id": "A", "text": "Baş Rahip'e gidip endişelerini dile getir."},
                {"id": "B", "text": "Tapınak arşivlerine inip eski kehanetleri araştır."},
                {"id": "C", "text": "Güvendiğin bir Leporim şifacısına mesaj gönderip onun fikrini al."}
            ],
             "current_location_id": "ak_noctis_start_tower"
        },
        "leporim": {
            "text": "Yeşil Tarlalar Birliği'nin lideri olarak, kuraklığın vurduğu tarlalarına bakıyorsun. Stoklar azalıyor ve Vargar'ın 'koruma' talepleri artıyor. Gençler silahlanmaktan bahsediyor. Bir yol bulmalısın. Ne yaparsın?",
            "choices": [
                {"id": "A", "text": "Acil durum konseyi toplayıp durumu tartış."},
                {"id": "B", "text": "Noctis bilgelerinden yardım veya kehanet istemek için yola çık."},
                {"id": "C", "text": "Kalan son ilaçları kullanarak gizli bir su kaynağı bulmaya çalış."}
            ],
             "current_location_id": "ak_leporim_start_fields"
        }
    },
    "dark_fantasy": {
        "ashen_legion": {
            "text": "Yıkık kalenin avlusunda, paslı zırhının içinde nöbet tutuyorsun. Yüzlerce yıldır olduğu gibi... Uzaktan gelen çığlıklar ve Kadim Kült'ün ayin şarkıları gecenin sessizliğini bozuyor. Lanetli görevin seni çağırıyor mu, yoksa bu gece farklı mı olacak? Ne yaparsın?",
            "choices": [
                {"id": "A", "text": "Seslerin geldiği yöne doğru ilerle ve tehdidi araştır."},
                {"id": "B", "text": "Kaledeki diğer Lejyon üyelerini uyar."},
                {"id": "C", "text": "Nöbet yerinde kal ve emirlere uy."}
            ],
             "current_location_id": "df_ashen_start_castle"
        },
        "shadow_syndicate": {
            "text": "Şehrin lağım kokan arka sokaklarındaki gizli buluşma noktasındasın. Yeni bir 'iş' teklifi aldın: Kadim Kült'ün elindeki güçlü bir artefaktı çalmak. Ödeme iyi, ama risk çok büyük. Ne yaparsın?",
            "choices": [
                {"id": "A", "text": "İşi kabul et ve plan yapmaya başla."},
                {"id": "B", "text": "Daha fazla bilgi almak için bağlantılarınla konuş."},
                {"id": "C", "text": "İşi reddet, bu kadar tehlikeli bir işe bulaşmak istemiyorsun."}
            ],
             "current_location_id": "df_shadow_start_alleys"
        },
        "primordial_cult": {
            "text": "Yeraltı tapınağının nemli duvarları, kurban kanıyla ve anlaşılmaz sembollerle kaplı. Efendilerin fısıltıları zihninde yankılanıyor, büyük bir ritüelin zamanının geldiğini söylüyorlar. Ancak Gölge Sendikası'ndan bir casusun etrafta dolaştığına dair söylentiler var. Ne yaparsın?",
            "choices": [
                {"id": "A", "text": "Ritüele hazırlanmaya başla, fısıltılara güven."},
                {"id": "B", "text": "Tapınağın etrafındaki güvenliği artır ve casusu ara."},
                {"id": "C", "text": "Daha fazla güç için küçük bir adak gerçekleştir."}
            ],
             "current_location_id": "df_cult_start_temple"
        }
    }
}


# --- Player Character Template ---
player_character_template = {
    "name": "Oyuncu",
    "class": None, # Seçilen ırk/fraksiyon adı buraya gelecek
    "world_id": None, 
    "world_name_display": None, 
    "stats": {
        "STR": 5, "END": 5, "WILL": 5, "ARC": 5, # Generic defaults
        # Animal Kingdom specific stats could be: AGI, INS, CUN, CHA
    },
    "inventory": [],
    "skills": [],
    "health": 100, 
    "current_location_id": None, # Başlangıç senaryosundan alınacak
    "history": [] 
}

# --- Class/Faction Base Stats ---
# Note: Keys here MUST match the race/faction IDs used in starting_scenarios and data attributes in HTML
class_base_stats = {
    "dark_fantasy": {
        "ashen_legion": {"STR": 8, "END": 7, "WILL": 6, "ARC": 2, "skills": ["Ölümsüz Saldırı"]},
        "shadow_syndicate": {"STR": 4, "END": 5, "WILL": 5, "ARC": 7, "skills": ["Gizli Hançer"]}, # Assuming ARC relates to cunning/forbidden knowledge
        "primordial_cult": {"STR": 5, "END": 6, "WILL": 8, "ARC": 4, "skills": ["Kaos Büyüsü"]} # Assuming WILL relates to resisting madness/channeling power
    },
    "animal_kingdom": {
        # Using race IDs from HTML data attributes
        "vargar": {"STR": 7, "END": 6, "INS": 5, "AGI": 6, "skills": ["Sürü Saldırısı"]}, # Example stats
        "vulpex": {"STR": 4, "END": 5, "INS": 6, "AGI": 7, "skills": ["Tuzak Kurma"]}, # Example stats
        "noctis": {"STR": 3, "END": 4, "INS": 8, "AGI": 5, "skills": ["Kehanet Fısıltısı"]}, # Example stats
        "leporim": {"STR": 4, "END": 6, "INS": 4, "AGI": 8, "skills": ["Kaçış Ustası"]} # Example stats
        # Redefined stats for Animal Kingdom: STR, END, INS (Instinct), AGI (Agility)
    }
}
