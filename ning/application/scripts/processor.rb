require File.dirname(__FILE__) + "/../db.rb"

# Function for processing a single file
def process(file) 
  File.open(file, "r") do |fh|
    # Create the new product
    product = Product.create
    while (line = fh.gets)
      # Parse object type, fields
      object_name, field_string = line.split(":")
      fields = {}
      field_string.split(",").each do |kv_pair|
        key, value = kv_pair.split("=")
        fields[key] = value
      end
      
      # Names, details, tags, photos, purchase points      
      if object_name == "tag"
        if fields.keys.size == 1
          product.name = fields["name"]
        elsif fields["type"] == "details"
          product.description = fields["name"]
        else 
          tag = Tag.first(:name => fields["name"], :type => fields["type"])
          unless tag
            tag = Tag.create
            tag.name = fields.delete("name")
            tag.type = fields.delete("type")
            tag.meta = fields
            tag.save
          end
          product.tags << tag
        end
      elsif object_name == "photo"
        # Don't take in duplicates (happens with optimized images)
        fields["url"] = fields["url"].split("%3F").first
        product.photos << Photo.create(fields) unless Photo.first(:url => fields["url"])
      elsif object_name == "purchase_point"
        unless product.purchase_points.first(fields)    
          product.purchase_points << PurchasePoint.create(fields)
        end
      else
        puts "Unknown: #{object_name} #{fields.to_json}"
      end
    end
    if Product.first(:name => product.name)
      product.destroy
    else
      product.save
    end
  end  
end


# Begin Main Program

# Validate arguments
unless ARGV.length > 0 and File.exists?(ARGV[0])
  puts "Invalid directory"
  exit 1
end
  
# Grab all files from the specified directory and process them
dir = ARGV[0]
Dir.entries(ARGV[0]).each do |file| 
  process("#{dir}/#{file}") unless ["..", ".", ".DS_Store"].include?(file)
end

# Log results to STDOU
puts "#{Product.all.count} products"
puts "#{Photo.all.count} photos"
puts "#{Tag.all.count} tags"
puts "#{PurchasePoint.all.count} purchase points"
  
