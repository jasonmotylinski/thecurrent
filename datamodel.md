```mermaid
erDiagram
songs {
    id VARCHAR(100)
    artist VARCHAR(255)
    title VARCHAR(255)
    album text
    played_at datetime
    duration text
    service_id int 
    song_id int
    play_id int 
    composer text 
    conductor text 
    orch_ensemble text 
    soloist_1 text
    soloist_2 text 
    soloist_3 text 
    soloist_4 text
    soloist_5 text 
    soloist_6 text 
    record_co text 
    record_id int 
    addl_text text 
    broadcast bool 
    songs_on_album text
    songs_by_artist text 
    album_mbid text
    art_url text
    year int
    month int 
    day int
    day_of_week VARCHAR(25)
    week int
    hour int
}

songs_metadata{
    id VARCHAR(255)
    artist VARCHAR(255)
    title VARCHAR(255)
    first_release_date DATE
}

shows{
    id integer
    host_name text
    show_name text
    start_time datetime
    end_time datetime
}

calendar {
    year integer
    month integer
    day integer
    hour integer
    day_of_week text
    week_of_year integer
}

artist_genres {
    artist VARCHAR(255)
    genre VARCHAR(255)
    source VARCHAR(255)
}

artist_metadata {
    artist VARCHAR(255)
}

artist_images {
    artist VARCHAR(255)
    height integer
    width integer
    url VARCHAR(255)
    source VARCHAR(255)
}

services {
    service_id integer
    name VARCHAR(255)
}

songs }|--o| songs_metadata: has_zero_to_one

artist_metadata ||--o{ songs: one_to_many
artist_metadata ||--o{ artist_genres: one_to_many
artist_metadata ||--o{ artist_images: one_to_many

services ||--o{ songs:one_to_many
```
