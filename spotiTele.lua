started = 0
our_id = 0

function vardump(value, depth, key)
  local linePrefix = ""
  local spaces = ""
  
  if key ~= nil then
    linePrefix = "["..key.."] = "
  end
  
  if depth == nil then
    depth = 0
  else
    depth = depth + 1
    for i=1, depth do spaces = spaces .. "  " end
  end
  
  if type(value) == 'table' then
    mTable = getmetatable(value)
    if mTable == nil then
      print(spaces ..linePrefix.."(table) ")
    else
      print(spaces .."(metatable) ")
        value = mTable
    end		
    for tableKey, tableValue in pairs(value) do
      vardump(tableValue, depth, tableKey)
    end
  elseif type(value)	== 'function' or 
      type(value)	== 'thread' or 
      type(value)	== 'userdata' or
      value		== nil
  then
    print(spaces..tostring(value))
  else
    print(spaces..linePrefix.."("..type(value)..") "..tostring(value))
  end
end

print ("HI, this is lua script")

function ok_cb(extra, success, result)
end


function on_msg_receive (msg)
  if started == 0 then
    return
  end
  if msg.out then
    return
  end
  if msg.text then
    mark_read (msg.from.print_name, ok_cb, false)
    os.execute("echo "..msg.text..">> telegram.log")
    --os.execute("/home/pi/showRandomPic.py")
  end
  if msg.media then    
    load_photo(msg.id, ok_cb, false)
    send_msg (msg.from.print_name,'irgendwas is immer',ok_cb,false)
    os.execute("/home/pi/showLatestPic.py")
  end
  if (msg.text == 'ls') then
    send_msg (msg.from.print_name, 'kommt sofort kleiner... wieso ist diese nachricht eigentlich langsamer???', ok_cb, false)
    -- os.execute("/home/pi/sendTelegram.sh "..msg.from.print_name.." /home/pi/playlist.txt")
    send_text (msg.from.print_name,"/home/pi/playlist.txt", ok_cb, false)
    return
  elseif(msg.text == 'playlist') then
    send_msg (msg.from.print_name, 'das wollen die leute', ok_cb, false)
    os.execute("/home/pi/sendTelegram.sh "..msg.from.print_name.." /home/pi/yay.txt")
    return
  elseif(msg.text == 'hilfe') then
    send_msg (msg.from.print_name, 'einfach etwas eingeben und das gefundene lied wird an das ende der playlist gesetzt // ls zeigt die aktuelle playlist // n spielt den naechsten song // + am ende spielt den eingegebenen song als naechsten // @ am ende fuegt ein ganzes album hinzu // ! am ende spielt den song sofort und loescht die aktuelle playlist, also vorischt mein guter...', ok_cb, false)
    return
  elseif(msg.text == 'hallo') then
    send_msg (msg.from.print_name, 'was liegt an senor?', ok_cb, false)
    return
  elseif(msg.text == 'reboot spotipy') then
    send_msg (msg.from.print_name, 'was hat der kleine denn jetzt schon wieder???', ok_cb, false)
    --os.execute("killall python*")
    os.execute("sudo reboot")
    return
  elseif(msg.text == 'knarre') then
    send_msg (msg.from.print_name, 'dann schau ma fein '..msg.id, ok_cb, false)
    send_photo(msg.from.print_name, "/home/pi/franzl_knarre_klein.jpg", ok_cb, false)
    os.execute("fbi -noverbose /home/pi/franzl_knarre_klein.jpg; sleep 10; killall fbi")
    return
  elseif(msg.text == 'photo') then
    send_msg (msg.from.print_name, 'licht aus glotze an', ok_cb, false)
    os.execute("/home/pi/showLatestPic.py")
    return
  elseif(msg.text == 'photos') then
    send_msg (msg.from.print_name, 'licht aus glotze an', ok_cb, false)
    os.execute("sudo killall fbi; sudo fbi -d /dev/fb0 -T 1 -t 10 -a -noverbose /home/pi/.telegram-cli/downloads/*")
    return
  elseif(msg.text == 'LAUTER') then
    send_msg (msg.from.print_name, 'jetzt gehts rund', ok_cb, false)
    os.execute("sudo amixer set PCM -- 400+")
    return
  elseif(msg.text == 'pssst') then
    send_msg (msg.from.print_name, 'die stille kennt die wahrheit', ok_cb, false)
    os.execute("sudo amixer set PCM -- 400-")
    return
  else
    send_msg (msg.from.print_name, 'gute wahl '..msg.from.print_name..'! spiele ich sofort...', ok_cb, false)
    os.execute("echo "..msg.from.print_name.." >> /home/pi/yay.txt")
    os.execute("echo "..msg.text.." >> /home/pi/yay.txt")
  end
end

function on_our_id (id)
  our_id = id
end

function on_user_update (user, what)
  --vardump (user)
end

function on_chat_update (chat, what)
  --vardump (chat)
end

function on_secret_chat_update (schat, what)
  --vardump (schat)
end

function on_get_difference_end ()
end

function cron()
  -- do something
  postpone (cron, false, 1.0)
end

function on_binlog_replay_end ()
  started = 1
  postpone (cron, false, 1.0)
end
