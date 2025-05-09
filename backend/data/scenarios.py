# -*- coding: utf-8 -*-

# --- Race/Faction Specific Starting Scenarios ---
STARTING_SCENARIOS = {
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

# --- Generic Initial Scenarios (Fallback) ---
# These are used if no specific class/faction is selected during game start
INITIAL_SCENARIOS_BY_WORLD = {
    "dark_fantasy": {
        "world_name_display": "Karanlık Fantezi Dünyası",
        "world_id": "dark_fantasy",
        "text": "Kara sislerin sardığı lanetli krallıkta, çatlamış bir yol ayrımındasın. Solunda, kemiklerle dolu bir çukur; sağında, kırık zincirlerinden sıyrılmış bir 'Yarı-Ölü' seni işaret parmağıyla çağırıyor. Arkanda ise homurdanan bir Canavarlar sürüsü yaklaşıyor. Ne yaparsın?",
        "choices": [
            {"id": "A", "text": "Yarı-Ölü'nün peşinden git."},
            {"id": "B", "text": "Kemik çukuruna atla."},
            {"id": "C", "text": "Canavarlarla savaşmayı göze al."}
        ],
        "current_location_id": "df_crossroads_01"
    },
    "animal_kingdom": {
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
}

# Helper function (optional)
def get_starting_scenario(world_id: str, class_faction_id: str = None) -> dict:
    """
    Retrieves the appropriate starting scenario.
    Falls back to generic world start if specific class/faction scenario is not found.
    """
    if class_faction_id and \
       world_id in STARTING_SCENARIOS and \
       class_faction_id in STARTING_SCENARIOS[world_id]:
        return STARTING_SCENARIOS[world_id][class_faction_id]
    else:
        # Fallback to generic scenario for the world
        return INITIAL_SCENARIOS_BY_WORLD.get(world_id, {}) # Return empty dict if world not found
